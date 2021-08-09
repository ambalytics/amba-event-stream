# amba-event-stream

[![PyPI][]][1]

  [PyPI]: https://img.shields.io/pypi/v/amba-event-stream
  [1]: https://pypi.org/project/amba-event-stream/

amba analytics event stream python package that connects to kafka to produce/connect or process events.

# Installation

``` bash
pip install amba-event-stream
```

# Releasing

Releases are published automatically when a tag is pushed to GitHub.

``` bash
# Set next version number
export RELEASE=x.x.x

# Create tags
git commit --allow-empty -m "Release $RELEASE"
git tag -a $RELEASE -m "Version $RELEASE"

# Push
git push upstream --tags
```
