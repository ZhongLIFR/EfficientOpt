"""Fixed, isolated Gurobi 13 executor for candidate and baseline builders."""
from __future__ import annotations
import argparse, ctypes, importlib.util, json, os, sys, time
from pathlib import Path
from typing import Any, Callable

# The license location is intentionally not embedded in the release.
# Set GRB_LICENSE_FILE in the local execution environment when needed.

import gurobipy as gp

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psutil = None

STATUS_NAMES={value:name for name,value in vars(gp.GRB).items() if name in {"LOADED","OPTIMAL","INFEASIBLE","INF_OR_UNBD","UNBOUNDED","CUTOFF","ITERATION_LIMIT","NODE_LIMIT","TIME_LIMIT","SOLUTION_LIMIT","INTERRUPTED","NUMERIC","SUBOPTIMAL","INPROGRESS","USER_OBJ_LIMIT"}}

def attr(model: gp.Model, name: str, default: Any=None) -> Any:
 try:
  value=model.getAttr(name); return default if value is None else value
 except (AttributeError,gp.GurobiError,TypeError,ValueError): return default

def load_builder(path: Path) -> Callable[[dict[str,Any]],Any]:
 candidate_dir=str(path.parent.resolve())
 if candidate_dir not in sys.path:
  sys.path.insert(0,candidate_dir)
 spec=importlib.util.spec_from_file_location("candidate_model",path)
 if spec is None or spec.loader is None: raise RuntimeError(f"Cannot import {path}")
 module=importlib.util.module_from_spec(spec); sys.modules["candidate_model"]=module; spec.loader.exec_module(module)
 builder=getattr(module,"build_model",None)
 if callable(builder): return builder
 iterator=getattr(module,"iter_models",None)
 if callable(iterator): return iterator
 raise TypeError("candidate_model.py must define callable build_model(instance) or iter_models(instance)")

def memory_snapshot(model: gp.Model) -> tuple[float|None,float|None]:
 current=attr(model,"MemUsed"); peak=attr(model,"MaxMemUsed")
 return (float(current) if isinstance(current,(int,float)) else None,float(peak) if isinstance(peak,(int,float)) else None)

def rss_mb() -> float | None:
    """Return process RSS in MB, using psutil or the Windows Working Set API."""
    try:
        if psutil is not None:
            return float(psutil.Process(os.getpid()).memory_info().rss) / (1024.0 * 1024.0)
    except Exception:
        pass
    if os.name == "nt":
        try:
            class Counters(ctypes.Structure):
                _fields_ = [("cb", ctypes.c_ulong), ("page_fault_count", ctypes.c_ulong),
                            ("peak_working_set_size", ctypes.c_size_t), ("working_set_size", ctypes.c_size_t),
                            ("quota_peak_paged_pool_usage", ctypes.c_size_t), ("quota_paged_pool_usage", ctypes.c_size_t),
                            ("quota_peak_non_paged_pool_usage", ctypes.c_size_t), ("quota_non_paged_pool_usage", ctypes.c_size_t),
                            ("pagefile_usage", ctypes.c_size_t), ("peak_pagefile_usage", ctypes.c_size_t)]
            counters = Counters()
            counters.cb = ctypes.sizeof(Counters)
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ok = ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
            if ok:
                return float(counters.working_set_size) / (1024.0 * 1024.0)
        except Exception:
            pass
    return None

def blank_result() -> dict[str,Any]:
 return {"solver_status":"ERROR","error_stage":None,"objective_value":None,"build_s":None,"solver_runtime_seconds":None,"solver_wall_s":None,"solver_s":None,"total_s":None,"num_variables":None,"num_constraints":None,"num_nonzeros":None,"num_binary_variables":None,"num_integer_variables":None,"num_continuous_variables":None,"node_count":None,"simplex_iterations":None,"work_units":None,"mip_gap":None,"rss_build_start_mb":None,"rss_before_solve_mb":None,"rss_after_solve_mb":None,"rss_max_snapshot_mb":None,"build_memory_delta_mb":None,"solve_memory_delta_mb":None,"gurobi_mem_used_mb":None,"gurobi_max_mem_used_mb":None,"gurobi_mem_after_build_gb":None,"gurobi_max_mem_after_build_gb":None,"gurobi_mem_after_solve_gb":None,"gurobi_max_mem_after_solve_gb":None,"gurobi_build_peak_above_current_gb":None,"gurobi_peak_increase_during_solve_gb":None,"gurobi_solve_extra_peak_gb":None,"notes":""}

def save(path: Path,result: dict[str,Any]) -> None:
 path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix(path.suffix+".tmp"); temp.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8"); os.replace(temp,path)

def _sum_numeric(values: list[Any]) -> float | int | None:
 numeric = [value for value in values if isinstance(value, (int, float))]
 if not numeric:
  return None
 total = sum(numeric)
 return int(total) if all(isinstance(value, int) for value in numeric) else float(total)


def run_builder(builder: Callable[[dict[str,Any]],Any],instance: dict[str,Any],result_path: Path) -> dict[str,Any]:
 start=time.perf_counter(); result=blank_result(); models=[]
 rss_start=rss_mb(); result["rss_build_start_mb"]=rss_start
 try:
  build_start=time.perf_counter(); built=builder(instance)
  if isinstance(built,gp.Model):
   models=[built]; aggregation="single_model"
  else:
   try: models=list(built)
   except TypeError as exc: raise TypeError("model builder must return a gurobipy.Model or iter_models(instance) iterable") from exc
   if not models: raise TypeError("iter_models(instance) must yield at least one gurobipy.Model")
   aggregation="iter_models"
  if not all(isinstance(model,gp.Model) for model in models):
   raise TypeError("iter_models(instance) must yield only gurobipy.Model objects")
  for model in models:
   model.resetParams()
   model.setParam("OutputFlag", 0); model.setParam("Threads", 1); model.setParam("Seed", 0); model.setParam("MIPGap", 0); model.setParam("TimeLimit", 5400)
   model.update()
  build_s=time.perf_counter()-build_start
  rss_before=rss_mb()
  build_memory=[memory_snapshot(model) for model in models]
  build_current=[current for current,_ in build_memory if current is not None]
  build_peak=[peak for _,peak in build_memory if peak is not None]
  mem_build=max(build_current) if build_current else None
  max_build=max(build_peak) if build_peak else None
  result.update({"build_s":build_s,"rss_before_solve_mb":rss_before,"build_memory_delta_mb":rss_before-rss_start if rss_before is not None and rss_start is not None else None,"gurobi_mem_after_build_gb":mem_build,"gurobi_max_mem_after_build_gb":max_build,"num_variables":int(sum(int(attr(model,"NumVars",0) or 0) for model in models)),"num_constraints":int(sum(int(attr(model,"NumConstrs",0) or 0) for model in models)),"num_nonzeros":int(sum(int(attr(model,"NumNZs",0) or 0) for model in models)),"num_binary_variables":int(sum(int(attr(model,"NumBinVars",0) or 0) for model in models)),"num_integer_variables":int(sum(int(attr(model,"NumIntVars",0) or 0) for model in models))})
  result["num_continuous_variables"]=result["num_variables"]-result["num_integer_variables"]
  save(result_path,result)
  runtimes=[]; solve_walls=[]; statuses=[]; solution_counts=[]; objectives=[]; solve_memory=[]; rss_values=[value for value in (rss_start,rss_before) if value is not None]
  for model in models:
   solve_start=time.perf_counter(); model.optimize(); solve_walls.append(time.perf_counter()-solve_start)
   runtimes.append(float(attr(model,"Runtime",0.0) or 0.0)); statuses.append(int(attr(model,"Status",-1))); solution_counts.append(int(attr(model,"SolCount",0) or 0))
   if solution_counts[-1]: objectives.append(float(attr(model,"ObjVal")))
   rss_after=rss_mb();
   if rss_after is not None: rss_values.append(rss_after)
   solve_memory.append(memory_snapshot(model))
  rss_after=rss_values[-1] if rss_values else None
  current_memory=[current for current,_ in solve_memory if current is not None]; peak_memory=[peak for _,peak in solve_memory if peak is not None]
  mem_solve=max(current_memory) if current_memory else None; max_solve=max(peak_memory) if peak_memory else None
  optimal=all(status==gp.GRB.OPTIMAL for status in statuses)
  status=gp.GRB.OPTIMAL if optimal else next((value for value in statuses if value!=gp.GRB.OPTIMAL),statuses[0])
  objective=sum(objectives) if len(objectives)==len(models) else None
  mip_gaps=[attr(model,"MIPGap") for model in models if int(attr(model,"SolCount",0) or 0)>0 and isinstance(attr(model,"MIPGap"), (int,float))]
  build_peak_delta=max_build-mem_build if max_build is not None and mem_build is not None else None
  solve_peak_delta=max_solve-max_build if max_solve is not None and max_build is not None else None
  extra_peak=max_solve-mem_build if max_solve is not None and mem_build is not None else None
  result.update({"solver_status":STATUS_NAMES.get(status,f"UNKNOWN({status})"),"objective_value":objective,"solver_runtime_seconds":float(sum(runtimes)),"solver_wall_s":float(sum(solve_walls)),"solver_s":float(sum(runtimes)),"total_s":build_s+float(sum(runtimes)),"node_count":_sum_numeric([attr(model,"NodeCount") for model in models]),"simplex_iterations":_sum_numeric([attr(model,"IterCount") for model in models]),"work_units":_sum_numeric([attr(model,"Work") for model in models]),"mip_gap":max(mip_gaps) if mip_gaps else (0.0 if optimal else None),"rss_after_solve_mb":rss_after,"rss_max_snapshot_mb":max(rss_values) if rss_values else None,"solve_memory_delta_mb":rss_after-rss_before if rss_after is not None and rss_before is not None else None,"gurobi_mem_used_mb":mem_solve*1024.0 if mem_solve is not None else None,"gurobi_max_mem_used_mb":max_solve*1024.0 if max_solve is not None else None,"gurobi_mem_after_solve_gb":mem_solve,"gurobi_max_mem_after_solve_gb":max_solve,"gurobi_build_peak_above_current_gb":build_peak_delta,"gurobi_peak_increase_during_solve_gb":solve_peak_delta,"gurobi_solve_extra_peak_gb":extra_peak,"notes":f"models={len(models)}; sol_count={sum(solution_counts)}; aggregation={aggregation}; runtime_source=Model.Runtime"})
 except Exception as exc:
  result["error_stage"]="build_or_solve"
  result["notes"]=f"{type(exc).__name__}: {exc}"
 finally:
  result["total_process_s"]=time.perf_counter()-start; save(result_path,result)
  for model in models:
   try:model.dispose()
   except Exception:pass
 return result

def run(candidate_path: Path,instance_path: Path,result_path: Path) -> dict[str,Any]:
 start=time.perf_counter()
 try:
  with instance_path.open(encoding="utf-8-sig") as handle: instance=json.load(handle)
 except Exception as exc:
  result=blank_result(); result.update({"error_stage":"load_instance","notes":f"{type(exc).__name__}: {exc}","total_process_s":time.perf_counter()-start}); save(result_path,result); return result
 try:
  builder=load_builder(candidate_path)
 except Exception as exc:
  result=blank_result(); result.update({"error_stage":"load_builder","notes":f"{type(exc).__name__}: {exc}","total_process_s":time.perf_counter()-start}); save(result_path,result); return result
 return run_builder(builder,instance,result_path)

def main() -> int:
 parser=argparse.ArgumentParser(); parser.add_argument("--candidate",type=Path,required=True); parser.add_argument("--instance",type=Path,required=True); parser.add_argument("--result",type=Path,required=True); args=parser.parse_args()
 result=run(args.candidate,args.instance,args.result); print("EXECUTION_RESULT_JSON="+json.dumps(result,ensure_ascii=False),flush=True)
 return 0 if result["solver_status"]!="ERROR" else 1

if __name__=="__main__": raise SystemExit(main())
