# Drift 

**Drift**: the cluster aware media re-encoding daemon

Drift monitors a shared directory for files to convert, converts them to the specified format, copies the converted file to an output directory, and finally deletes the original file. Multiple instances of drift can be started, either on the same machine or on a networked cluster of machines. Drift instances coordinate their efforts using etcd for distributed locking, and configuration.

## Prereqs

Drift requires a working installation of `ffmpeg` and `ffprobe` for file conversion. For clustering a `etcd` daemon needs to be provided.

## Installation

Simply clone the repo and install the dependencies.
```
git clone https://github.com/tmacro/drift
cd drift
pip -r requirements.txt
```
or pull the docker image
```
docker pull tmacro/drift
```

## Configuration

All configuration is handled in the top level config.yaml file.


## License

Drift is released under the BSD 3-Clause license.

```
BSD 3-Clause License

Copyright (c) 2018, Taylor McKinnon
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```
