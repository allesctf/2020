#!/bin/bash
git clone https://github.com/ammaraskar/pyCraft.git
cd pyCraft
git checkout 3c84c2a42986afbc13f049b1779816b358d28eeb
git apply ../pyCraft_patch.diff
