#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

#CONFIGS="base alloy unison tpc tpc-random-3 footprint"
#CONFIGS="base footprint tidy-default tidy-default-70 tidy-default-60"
#CONFIGS="base footprint tidy-new base-100s footprint-100s tidy-100s base-150s footprint-150s tidy-150s base-250s footprint-250s tidy-250s"
CONFIGS="base-100s-INSINTER footprint-100s-INSINTER tidy-100s-INSINTER"
#APPS="
#spec-mix_403.gcc-433.milc-429.mcf-403.gcc-462.libquantum-429.mcf-459.GemsFDTD-482.sphinx3_100
#spec-mix_403.gcc-433.milc-429.mcf-459.GemsFDTD-470.lbm-403.gcc-450.soplex-459.GemsFDTD_100
#spec-mix_403.gcc-433.milc-450.soplex-403.gcc-433.milc-450.soplex-462.libquantum-429.mcf_100
#spec-mix_403.gcc-433.milc-450.soplex-429.mcf-470.lbm-482.sphinx3-403.gcc-470.lbm_100
#spec-mix_403.gcc-433.milc-450.soplex-459.GemsFDTD-470.lbm-429.mcf-470.lbm-482.sphinx3_100
#spec-mix_403.gcc-433.milc-450.soplex-470.lbm-450.soplex-462.libquantum-429.mcf-470.lbm_100
#spec-mix_403.gcc-433.milc-450.soplex-471.omnetpp-450.soplex-471.omnetpp-429.mcf-470.lbm_100
#spec-mix_403.gcc-433.milc-450.soplex-482.sphinx3-403.gcc-433.milc-459.GemsFDTD-482.sphinx3_100
#spec-mix_403.gcc-433.milc-462.libquantum-470.lbm-433.milc-450.soplex-471.omnetpp-459.GemsFDTD_100
#spec-mix_403.gcc-433.milc-482.sphinx3-433.milc-429.mcf-459.GemsFDTD-470.lbm-482.sphinx3_100
#spec-mix_403.gcc-450.soplex-429.mcf-482.sphinx3-403.gcc-450.soplex-429.mcf-459.GemsFDTD_100
#spec-mix_403.gcc-450.soplex-462.libquantum-403.gcc-429.mcf-459.GemsFDTD-470.lbm-482.sphinx3_100
#spec-mix_403.gcc-450.soplex-462.libquantum-429.mcf-459.GemsFDTD-482.sphinx3-433.milc-470.lbm_100
#spec-mix_403.gcc-450.soplex-462.libquantum-459.GemsFDTD-470.lbm-403.gcc-462.libquantum-470.lbm_100
#spec-mix_403.gcc-450.soplex-471.omnetpp-429.mcf-459.GemsFDTD-470.lbm-403.gcc-462.libquantum_100
#spec-mix_403.gcc-450.soplex-471.omnetpp-459.GemsFDTD-470.lbm-433.milc-459.GemsFDTD-470.lbm_100
#spec-mix_403.gcc-450.soplex-471.omnetpp-482.sphinx3-403.gcc-462.libquantum-459.GemsFDTD-470.lbm_100
#spec-mix_403.gcc-459.GemsFDTD-433.milc-462.libquantum-471.omnetpp-429.mcf-459.GemsFDTD-482.sphinx3_100
#spec-mix_403.gcc-459.GemsFDTD-482.sphinx3-450.soplex-471.omnetpp-429.mcf-459.GemsFDTD-482.sphinx3_100
#spec-mix_403.gcc-462.libquantum-471.omnetpp-429.mcf-482.sphinx3-403.gcc-429.mcf-470.lbm_100
#spec-mix_403.gcc-471.omnetpp-429.mcf-459.GemsFDTD-470.lbm-482.sphinx3-403.gcc-433.milc_100
#spec-mix_403.gcc-471.omnetpp-470.lbm-482.sphinx3-471.omnetpp-429.mcf-459.GemsFDTD-470.lbm_100
#spec-mix_403.gcc-482.sphinx3-403.gcc-462.libquantum-471.omnetpp-429.mcf-459.GemsFDTD-470.lbm_100
#spec-mix_429.mcf-470.lbm-403.gcc-433.milc-462.libquantum-471.omnetpp-429.mcf-459.GemsFDTD_100
#spec-mix_433.milc-429.mcf-459.GemsFDTD-403.gcc-433.milc-462.libquantum-459.GemsFDTD-482.sphinx3_100
#spec-mix_433.milc-450.soplex-429.mcf-403.gcc-433.milc-471.omnetpp-459.GemsFDTD-470.lbm_100
#spec-mix_433.milc-450.soplex-429.mcf-403.gcc-450.soplex-471.omnetpp-470.lbm-482.sphinx3_100
#spec-mix_433.milc-450.soplex-433.milc-462.libquantum-471.omnetpp-459.GemsFDTD-470.lbm-482.sphinx3_100
#spec-mix_433.milc-450.soplex-459.GemsFDTD-482.sphinx3-403.gcc-459.GemsFDTD-470.lbm-482.sphinx3_100
#spec-mix_433.milc-450.soplex-459.GemsFDTD-482.sphinx3-433.milc-471.omnetpp-429.mcf-482.sphinx3_100
#spec-mix_433.milc-450.soplex-462.libquantum-429.mcf-459.GemsFDTD-433.milc-471.omnetpp-459.GemsFDTD_100
#spec-mix_433.milc-450.soplex-462.libquantum-459.GemsFDTD-403.gcc-433.milc-450.soplex-462.libquantum_100
#spec-mix_433.milc-450.soplex-462.libquantum-470.lbm-482.sphinx3-450.soplex-462.libquantum-429.mcf_100
#spec-mix_433.milc-450.soplex-462.libquantum-471.omnetpp-403.gcc-450.soplex-471.omnetpp-429.mcf_100
#spec-mix_433.milc-450.soplex-471.omnetpp-403.gcc-433.milc-462.libquantum-470.lbm-482.sphinx3_100
#spec-mix_433.milc-450.soplex-471.omnetpp-459.GemsFDTD-450.soplex-471.omnetpp-429.mcf-459.GemsFDTD_100
#spec-mix_433.milc-450.soplex-471.omnetpp-470.lbm-482.sphinx3-459.GemsFDTD-470.lbm-482.sphinx3_100
#spec-mix_433.milc-459.GemsFDTD-433.milc-462.libquantum-471.omnetpp-429.mcf-459.GemsFDTD-482.sphinx3_100
#spec-mix_433.milc-462.libquantum-471.omnetpp-429.mcf-470.lbm-433.milc-429.mcf-459.GemsFDTD_100
#spec-mix_433.milc-462.libquantum-471.omnetpp-470.lbm-482.sphinx3-471.omnetpp-429.mcf-482.sphinx3_100
#spec-mix_433.milc-470.lbm-403.gcc-433.milc-450.soplex-462.libquantum-471.omnetpp-459.GemsFDTD_100
#spec-mix_433.milc-471.omnetpp-459.GemsFDTD-470.lbm-482.sphinx3-403.gcc-450.soplex-482.sphinx3_100
#spec-mix_450.soplex-429.mcf-459.GemsFDTD-470.lbm-482.sphinx3-450.soplex-471.omnetpp-459.GemsFDTD_100
#spec-mix_450.soplex-429.mcf-470.lbm-482.sphinx3-471.omnetpp-429.mcf-459.GemsFDTD-470.lbm_100
#spec-mix_450.soplex-459.GemsFDTD-470.lbm-403.gcc-433.milc-462.libquantum-459.GemsFDTD-470.lbm_100
#spec-mix_450.soplex-462.libquantum-429.mcf-470.lbm-403.gcc-471.omnetpp-429.mcf-459.GemsFDTD_100
#spec-mix_450.soplex-462.libquantum-429.mcf-482.sphinx3-403.gcc-450.soplex-462.libquantum-482.sphinx3_100
#spec-mix_450.soplex-462.libquantum-459.GemsFDTD-470.lbm-482.sphinx3-433.milc-459.GemsFDTD-470.lbm_100
#spec-mix_450.soplex-462.libquantum-459.GemsFDTD-482.sphinx3-403.gcc-462.libquantum-471.omnetpp-482.sphinx3_100
#spec-mix_450.soplex-462.libquantum-471.omnetpp-429.mcf-482.sphinx3-471.omnetpp-470.lbm-482.sphinx3_100
#spec-mix_450.soplex-462.libquantum-482.sphinx3-403.gcc-450.soplex-462.libquantum-459.GemsFDTD-470.lbm_100
#spec-mix_450.soplex-470.lbm-450.soplex-462.libquantum-429.mcf-459.GemsFDTD-470.lbm-482.sphinx3_100
#spec-mix_450.soplex-471.omnetpp-429.mcf-459.GemsFDTD-470.lbm-433.milc-471.omnetpp-429.mcf_100
#spec-mix_450.soplex-471.omnetpp-433.milc-462.libquantum-471.omnetpp-459.GemsFDTD-470.lbm-482.sphinx3_100
#spec-mix_450.soplex-471.omnetpp-470.lbm-403.gcc-433.milc-450.soplex-429.mcf-459.GemsFDTD_100
#spec-mix_450.soplex-471.omnetpp-470.lbm-403.gcc-433.milc-450.soplex-459.GemsFDTD-470.lbm_100
#spec-mix_459.GemsFDTD-433.milc-450.soplex-471.omnetpp-429.mcf-459.GemsFDTD-470.lbm-482.sphinx3_100
#spec-mix_459.GemsFDTD-470.lbm-482.sphinx3-403.gcc-433.milc-450.soplex-462.libquantum-471.omnetpp_100
#spec-mix_462.libquantum-429.mcf-459.GemsFDTD-482.sphinx3-403.gcc-462.libquantum-429.mcf-482.sphinx3_100
#spec-mix_471.omnetpp-429.mcf-470.lbm-403.gcc-450.soplex-462.libquantum-429.mcf-459.GemsFDTD_100
#spec-mix_471.omnetpp-429.mcf-470.lbm-433.milc-450.soplex-462.libquantum-471.omnetpp-482.sphinx3_100
#spec-mix_471.omnetpp-433.milc-450.soplex-462.libquantum-471.omnetpp-429.mcf-459.GemsFDTD-482.sphinx3_100
#spec-mix_471.omnetpp-459.GemsFDTD-470.lbm-482.sphinx3-403.gcc-429.mcf-470.lbm-482.sphinx3_100
#spec-mix_471.omnetpp-470.lbm-482.sphinx3-433.milc-450.soplex-471.omnetpp-429.mcf-470.lbm_100
#dbt3_1_100
#dbt3_8_100
#bigmem-mix_graph500-nascg_100
#bigmem-mix_graph500-nasmg_100
#bigmem-mix_nascg-nasmg_100
#bigmem-mix_stream-graph500_100
#bigmem-mix_stream-nascg_100
#bigmem-mix_stream-nasmg_100
#bigmem_graph500_100
#bigmem_nascg_100
#bigmem_nasmg_100
#bigmem_stream_100
#spec-mix2_403.gcc-429.mcf-482.sphinx3-462.libquantum-459.GemsFDTD-482.sphinx3-482.sphinx3-471.omnetpp_100
#spec-mix2_403.gcc-429.mcf-482.sphinx3-471.omnetpp-450.soplex-450.soplex-462.libquantum-470.lbm_100
#spec-mix2_403.gcc-433.milc-450.soplex-429.mcf-470.lbm-482.sphinx3-429.mcf-403.gcc_100
#spec-mix2_403.gcc-450.soplex-462.libquantum-433.milc-403.gcc-433.milc-429.mcf-459.GemsFDTD_100
#spec-mix2_403.gcc-462.libquantum-429.mcf-482.sphinx3-459.GemsFDTD-433.milc-450.soplex-459.GemsFDTD_100
#spec-mix2_403.gcc-462.libquantum-482.sphinx3-471.omnetpp-459.GemsFDTD-470.lbm-429.mcf-429.mcf_100
#spec-mix2_429.mcf-450.soplex-470.lbm-403.gcc-433.milc-429.mcf-482.sphinx3-429.mcf_100
#spec-mix2_429.mcf-459.GemsFDTD-433.milc-462.libquantum-471.omnetpp-462.libquantum-459.GemsFDTD-470.lbm_100
#spec-mix2_429.mcf-482.sphinx3-450.soplex-429.mcf-482.sphinx3-462.libquantum-482.sphinx3-459.GemsFDTD_100
#spec-mix2_433.milc-450.soplex-450.soplex-462.libquantum-459.GemsFDTD-450.soplex-429.mcf-482.sphinx3_100
#spec-mix2_433.milc-450.soplex-462.libquantum-482.sphinx3-433.milc-462.libquantum-459.GemsFDTD-450.soplex_100
#spec-mix2_433.milc-459.GemsFDTD-403.gcc-403.gcc-450.soplex-470.lbm-482.sphinx3-459.GemsFDTD_100
#spec-mix2_433.milc-462.libquantum-429.mcf-462.libquantum-470.lbm-433.milc-450.soplex-429.mcf_100
#spec-mix2_433.milc-470.lbm-482.sphinx3-403.gcc-462.libquantum-403.gcc-471.omnetpp-450.soplex_100
#spec-mix2_433.milc-471.omnetpp-470.lbm-403.gcc-433.milc-471.omnetpp-482.sphinx3-450.soplex_100
#spec-mix2_433.milc-471.omnetpp-482.sphinx3-450.soplex-403.gcc-482.sphinx3-450.soplex-462.libquantum_100
#spec-mix2_450.soplex-403.gcc-462.libquantum-471.omnetpp-429.mcf-450.soplex-459.GemsFDTD-482.sphinx3_100
#spec-mix2_450.soplex-429.mcf-470.lbm-403.gcc-459.GemsFDTD-462.libquantum-471.omnetpp-482.sphinx3_100
#spec-mix2_450.soplex-462.libquantum-429.mcf-470.lbm-482.sphinx3-459.GemsFDTD-450.soplex-471.omnetpp_100
#spec-mix2_459.GemsFDTD-433.milc-471.omnetpp-450.soplex-482.sphinx3-403.gcc-450.soplex-482.sphinx3_100
#spec-mix2_459.GemsFDTD-470.lbm-482.sphinx3-459.GemsFDTD-470.lbm-403.gcc-450.soplex-482.sphinx3_100
#spec-mix2_462.libquantum-433.milc-462.libquantum-429.mcf-459.GemsFDTD-433.milc-459.GemsFDTD-470.lbm_100
#spec-mix2_462.libquantum-459.GemsFDTD-433.milc-462.libquantum-471.omnetpp-403.gcc-462.libquantum-429.mcf_100
#spec-mix2_462.libquantum-470.lbm-403.gcc-482.sphinx3-471.omnetpp-429.mcf-482.sphinx3-450.soplex_100
#spec-mix2_462.libquantum-470.lbm-450.soplex-462.libquantum-482.sphinx3-462.libquantum-403.gcc-459.GemsFDTD_100
#spec-mix2_462.libquantum-470.lbm-482.sphinx3-482.sphinx3-471.omnetpp-482.sphinx3-470.lbm-482.sphinx3_100
#spec-mix2_470.lbm-403.gcc-450.soplex-403.gcc-433.milc-459.GemsFDTD-470.lbm-482.sphinx3_100
#spec-mix2_470.lbm-450.soplex-462.libquantum-471.omnetpp-470.lbm-462.libquantum-471.omnetpp-429.mcf_100
#spec-mix2_470.lbm-462.libquantum-471.omnetpp-433.milc-450.soplex-462.libquantum-429.mcf-470.lbm_100
#spec-mix2_470.lbm-471.omnetpp-403.gcc-429.mcf-459.GemsFDTD-471.omnetpp-429.mcf-459.GemsFDTD_100
#spec-mix2_471.omnetpp-429.mcf-429.mcf-459.GemsFDTD-403.gcc-471.omnetpp-459.GemsFDTD-471.omnetpp_100
#spec-mix2_482.sphinx3-459.GemsFDTD-482.sphinx3-433.milc-462.libquantum-482.sphinx3-450.soplex-471.omnetpp_100
#APPS="
#dbt3_1_10
#dbt3_2_10
#dbt3_4_10
#dbt3_6_10
#dbt3_8_10
#"
APPS="
dbt3_4_10
"
#APPS="
#dbt2_16_10
#"
#APPS="
#dbt3_1_100
#dbt3_2_100
#dbt3_4_100
#dbt3_6_100
#dbt3_8_100
#"
#spec-mix3_403.gcc-433.milc-437.leslie3d-462.libquantum-429.mcf-470.lbm-429.mcf-459.GemsFDTD_100
#spec-mix3_403.gcc-433.milc-450.soplex-471.omnetpp-459.GemsFDTD-403.gcc-462.libquantum-462.libquantum_100
#spec-mix3_403.gcc-450.soplex-462.libquantum-459.GemsFDTD-470.lbm-437.leslie3d-462.libquantum-437.leslie3d_100
#spec-mix3_403.gcc-450.soplex-471.omnetpp-433.milc-462.libquantum-471.omnetpp-450.soplex-470.lbm_100
#spec-mix3_403.gcc-459.GemsFDTD-437.leslie3d-433.milc-462.libquantum-437.leslie3d-403.gcc-462.libquantum_100
#spec-mix3_403.gcc-471.omnetpp-429.mcf-403.gcc-462.libquantum-471.omnetpp-470.lbm-470.lbm_100
#spec-mix3_429.mcf-437.leslie3d-433.milc-450.soplex-471.omnetpp-462.libquantum-459.GemsFDTD-437.leslie3d_100
#spec-mix3_429.mcf-459.GemsFDTD-471.omnetpp-429.mcf-437.leslie3d-462.libquantum-459.GemsFDTD-470.lbm_100
#spec-mix3_433.milc-429.mcf-433.milc-462.libquantum-429.mcf-459.GemsFDTD-437.leslie3d-470.lbm_100
#spec-mix3_433.milc-429.mcf-437.leslie3d-403.gcc-471.omnetpp-437.leslie3d-462.libquantum-471.omnetpp_100
#spec-mix3_433.milc-437.leslie3d-470.lbm-403.gcc-433.milc-450.soplex-462.libquantum-429.mcf_100
#spec-mix3_433.milc-450.soplex-462.libquantum-470.lbm-433.milc-450.soplex-462.libquantum-459.GemsFDTD_100
#spec-mix3_433.milc-459.GemsFDTD-450.soplex-471.omnetpp-462.libquantum-462.libquantum-429.mcf-459.GemsFDTD_100
#spec-mix3_433.milc-459.GemsFDTD-470.lbm-403.gcc-459.GemsFDTD-462.libquantum-462.libquantum-429.mcf_100
#spec-mix3_433.milc-462.libquantum-459.GemsFDTD-437.leslie3d-462.libquantum-462.libquantum-462.libquantum-471.omnetpp_100
#spec-mix3_450.soplex-429.mcf-433.milc-450.soplex-470.lbm-471.omnetpp-459.GemsFDTD-470.lbm_100
#spec-mix3_450.soplex-429.mcf-462.libquantum-471.omnetpp-459.GemsFDTD-437.leslie3d-471.omnetpp-459.GemsFDTD_100
#spec-mix3_450.soplex-437.leslie3d-403.gcc-433.milc-450.soplex-459.GemsFDTD-433.milc-470.lbm_100
#spec-mix3_450.soplex-459.GemsFDTD-403.gcc-433.milc-471.omnetpp-437.leslie3d-470.lbm-437.leslie3d_100
#spec-mix3_450.soplex-462.libquantum-429.mcf-403.gcc-471.omnetpp-429.mcf-450.soplex-429.mcf_100
#spec-mix3_450.soplex-462.libquantum-437.leslie3d-462.libquantum-471.omnetpp-429.mcf-403.gcc-462.libquantum_100
#spec-mix3_450.soplex-462.libquantum-450.soplex-470.lbm-462.libquantum-462.libquantum-429.mcf-459.GemsFDTD_100
#spec-mix3_450.soplex-471.omnetpp-437.leslie3d-403.gcc-459.GemsFDTD-450.soplex-462.libquantum-429.mcf_100
#spec-mix3_459.GemsFDTD-470.lbm-433.milc-462.libquantum-470.lbm-450.soplex-462.libquantum-462.libquantum_100
#spec-mix3_462.libquantum-429.mcf-403.gcc-462.libquantum-459.GemsFDTD-470.lbm-437.leslie3d-433.milc_100
#spec-mix3_462.libquantum-429.mcf-459.GemsFDTD-470.lbm-462.libquantum-429.mcf-429.mcf-437.leslie3d_100
#spec-mix3_462.libquantum-462.libquantum-437.leslie3d-403.gcc-459.GemsFDTD-433.milc-429.mcf-437.leslie3d_100
#spec-mix3_462.libquantum-470.lbm-471.omnetpp-459.GemsFDTD-433.milc-462.libquantum-471.omnetpp-437.leslie3d_100
#spec-mix3_462.libquantum-471.omnetpp-450.soplex-462.libquantum-433.milc-450.soplex-462.libquantum-437.leslie3d_100
#spec-mix3_462.libquantum-471.omnetpp-459.GemsFDTD-471.omnetpp-429.mcf-470.lbm-437.leslie3d-471.omnetpp_100
#spec-mix3_462.libquantum-471.omnetpp-470.lbm-437.leslie3d-462.libquantum-429.mcf-470.lbm-433.milc_100
#spec-mix3_471.omnetpp-459.GemsFDTD-403.gcc-437.leslie3d-462.libquantum-471.omnetpp-429.mcf-437.leslie3d_100
#spec-r_403.gcc_100
#spec-r_410.bwaves_100
#spec-r_429.mcf_100
#spec-r_433.milc_100
#spec-r_437.leslie3d_100
#spec-r_450.soplex_100
#spec-r_459.GemsFDTD_100
#spec-r_462.libquantum_100
#spec-r_470.lbm_100
#spec-r_471.omnetpp_100
#spec-r_473.astar_100
#spec-r_482.sphinx3_100
#"
#spec_403.gcc_100
#spec_410.bwaves_100
#spec_429.mcf_100
#spec_433.milc_100
#spec_437.leslie3d_100
#spec_450.soplex_100
#spec_459.GemsFDTD_100
#spec_462.libquantum_100
#spec_470.lbm_100
#spec_471.omnetpp_100
#spec_473.astar_100
#spec_482.sphinx3_100
#"

#spec_400.perlbench spec_403.gcc spec_416.gamess spec_433.milc spec_435.gromacs spec_437.leslie3d spec_445.gobmk spec_450.soplex spec_454.calculix spec_458.sjeng spec_462.libquantum spec_465.tonto spec_471.omnetpp spec_483.xalancbmk spec_401.bzip2 spec_410.bwaves spec_429.mcf spec_434.zeusmp spec_436.cactusADM spec_444.namd spec_453.povray spec_456.hmmer spec_459.GemsFDTD spec_464.h264ref spec_470.lbm spec_473.astar spec_482.sphinx3
#spec-r_400.perlbench spec-r_403.gcc spec-r_416.gamess spec-r_433.milc spec-r_435.gromacs spec-r_437.leslie3d spec-r_445.gobmk spec-r_450.soplex spec-r_454.calculix spec-r_458.sjeng spec-r_462.libquantum spec-r_465.tonto spec-r_471.omnetpp spec-r_483.xalancbmk spec-r_401.bzip2 spec-r_410.bwaves spec-r_429.mcf spec-r_434.zeusmp spec-r_436.cactusADM spec-r_444.namd spec-r_453.povray spec-r_456.hmmer spec-r_459.GemsFDTD spec-r_464.h264ref spec-r_470.lbm spec-r_473.astar spec-r_482.sphinx3
#tpch_2 tpch_3 tpch_4 tpch_5 tpch_6 tpch_7 tpch_8 tpch_9 tpch_10 tpch_11 tpch_12 tpch_13 tpch_14 tpch_15 tpch_16 tpch_17 tpch_18 tpch_19 tpch_20 tpch_21 tpch_22
#dbt3_1 dbt3_2 dbt3_4 dbt3_8"

BASE=tests_zsim_
OUTFILE=/dev/stdout #$DIR/results_check.txt
RESDIR="/home/aarmejach/projects/AXLE/dbms-profiler/results-zsim"

date > $OUTFILE

for CONFIG in $CONFIGS; do
    echo "" >> $OUTFILE
    echo "Check for ${BASE}${CONFIG}" >> $OUTFILE
    echo "-------------------------------" >> $OUTFILE

    cd ${RESDIR}/${BASE}${CONFIG}

    for APP in $APPS; do
        #file=${APP}_100_
        file=${APP}_

        #Check if simterm file exists
        if [ ! -e ${file}simterm.txt ]; then
            echo "Zsim simterm file not found for ${file}, still running?" >> $OUTFILE
            continue
        fi

        #Check if GM memory allocation OK
        grep -i "gm_create failed" ${file}simterm.txt
        if [ $? -ne 1 ]; then
            echo "Zsim GM segment memory allocation failed for ${file}" >> $OUTFILE
            continue
        fi

        # Check if assert ocurred
        grep -i assert ${file}simterm.txt
        if [ $? -ne 1 ]; then
            #Match found, there is assert trigered
            echo "Assert found in simterm for ${file}" >> $OUTFILE
            continue
        fi

        # Check if assert ocurred
        grep -i assert ${file}zsim.log*
        if [ $? -ne 1 ]; then
            #Match found, there is assert trigered
            echo "Assert found in simterm for ${file}" >> $OUTFILE
            continue
        fi

        #Check for panic errors
        grep -i -e panic "${file}simterm.txt" /dev/null
        if [ $? -ne 1 ]; then
            echo "Panic error in ${file}" >> $OUTFILE
            continue
        fi

        #Check if zsim stats file exists
        if [ ! -e ${file}zsim.out ]; then
            echo "Zsim stats file not found for ${file}" >> $OUTFILE
            continue
        fi

        #Check if mem stats file exists
        if [ ! -e ${file}mem-0-nvmain.out ]; then
            echo "Mem stats file not found for ${file}" >> $OUTFILE
            continue
        fi

        #Check if mem stats file has proper size
        if [ $(stat -c%s "${file}mem-0-nvmain.out") -lt 100 ]; then
            echo "Mem stats file too small ${file}" >> $OUTFILE
            continue
        fi

        #Check if zsim stats file has proper size
        if [ $(stat -c%s "${file}zsim.out") -lt 100 ]; then
            echo "Zsim stats file too small ${file}" >> $OUTFILE
            continue
        fi

        #Check if mem stats is stale file
        if [ $(($(date -r ${file}simterm.txt +%s)-$(date -r ${file}mem-0-nvmain.out +%s))) -gt 30 ]; then
            echo "Mem stats file is STALE ${file}" >> $OUTFILE
            continue
        fi
        if [ $(($(date -r ${file}simterm.txt +%s)-$(date -r ${file}zsim.out +%s))) -gt 30 ]; then
            echo "Zsim stats file is STALE ${file}" >> $OUTFILE
            continue
        fi

        #Check for good termination
        grep "All children done" "${file}simterm.txt" > /dev/null
        if [ $? -eq 1 ]; then
            echo "WARN good termination not found for ${file}" >> $OUTFILE
            continue
        fi

    done
done
