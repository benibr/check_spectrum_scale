# checkmk\_spectrum\_scale

This script is a local check for checkMK that 
checks the status of a Spectrum Scale Cluster/Nodes (GPFS)

## Usage

```bash
# check health of the local node
./checkmk_spectrum_scale.py health

# check another node in the cluster
./checkmk_spectrum_scale.py health --node remote-host-01

# check health of a specific component
./checkmk_spectrum_scale.py health --component NETWORK
```

### Usage with checkMK

To use this check with checkMK simply put it in `/usr/lib/check_mk_agent/local/`,
make it executable and run the checkMK service discovery.
When run without arguments, the check will return the overall health of the local node.

You can also let the check create sibling checkfiles with different parameters which are
then also discoverable by checkMK

```bash
# create a check file for another node
./checkmk_spectrum_scale.py --create-check health --node remote-host-01
```

## Greetings

This repo used to be a fork of
[github.com/theGidy/check\_spectrum\_scale](https://github.com/theGidy/check_spectrum_scale/tree/master())
