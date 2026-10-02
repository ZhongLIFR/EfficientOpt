# EfficientOpt Numerical Instances

[Zenodo record / DOI: 10.5281/zenodo.23093476](https://doi.org/10.5281/zenodo.23093476) ·
[Download EfficientOpt-data.zip](https://zenodo.org/records/23093476/files/EfficientOpt-data.zip?download=1)

This archive contains all **624 numerical instances** accompanying
[Right Answers, Costly Models: The Efficiency Gap in LLM-based Optimization Modeling](https://arxiv.org/abs/2609.38884):

| Split | Instances | Scope |
| --- | ---: | --- |
| `main` | 561 | Main benchmark evaluated in the paper |
| `supplemental` | 63 | Additional technique coverage, outside the main evaluation |

`EfficientOpt-data.zip` is approximately 1.76 GB compressed and 7.52 GB after
extraction. It contains the actual numerical JSON files, an [index](index.csv),
and this README. The index records each task's split, technique, repository path,
reference objective where available, and instance SHA-256 hash.

```text
dataset/
  README.md
  index.csv
  main/Txx/Txx_nnn/instance.json
  supplemental/Txx/Txx_nnn/instance.json
```

## Use with the code

Clone the [EfficientOpt repository](https://github.com/ZhongLIFR/EfficientOpt),
then download and extract the archive from the repository root:

```bash
curl -L --fail "https://zenodo.org/records/23093476/files/EfficientOpt-data.zip?download=1" -o EfficientOpt-data.zip
unzip -n EfficientOpt-data.zip
```

The archive adds `instance.json` beside each task's `problem.md` and restores the
expected directory layout. The `-n` option keeps existing files. Problem
statements, reference implementations, and evaluation code are provided in the
GitHub repository.
