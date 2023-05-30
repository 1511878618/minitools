#!/usr/bin/env bash

usage() {
    cat >&1 <<-EOF

	请使用: $(basename $0) <option>

	可使用的参数 <option> 包括:
    -f/--bfile <bfile>  plink bfile prefix
    -c/--chain <chain>  liftOver chain file
    -e/--export <export>  export format,[bed|bgen-1.1|bgen-1.2] see plink2, note bed => make-bed in plink2 
    -t/--threads <threads>  threads
    -o/--out <out>  output prefix
	EOF
    exit 2
}
PARSED_ARGUMENTS=$(
    getopt -a -n alphabet -o b:c:e:t:o:rh --long bgenFile:,chain:,export:,threads:,out:,ref-first,help -- "$@"
)
VALID_ARGUMENTS=$?

if [ "$VALID_ARGUMENTS" != "0" ]; then
    usage
fi
eval set -- "$PARSED_ARGUMENTS"

#Default
ref_order=ref-last
export=bgen-1.2
while :; do
    case "$1" in
    -b | --bgenFile)
        bgenFile=$2
        shift 2
        ;;
    -c | --chain)
        chain=$2
        shift 2
        ;;
    -e | --export)
        export="$2"
        shift 2
        ;;
    -t | --threads)
        threads="$2"
        shift 2
        ;;
    -o | --out)
        out="$2"
        shift 2
        ;;
    -r | --ref-first)
        ref_order=ref-first
        shift
        ;;
    -h | --help)
        usage
        ;;
    # -- means the end of the arguments; drop this, and break out of the while loop
    --)
        shift
        break
        ;;
    # If invalid options were passed, then getopt should have reported an error,
    # which we checked as VALID_ARGUMENTS when getopt was called...
    *)
        echo "Unexpected option: $1 - this should not happen."
        usage
        ;;
    esac
done

# 检查必需的参数
if [[ -z "$bgenFile" ]]; then
    echo "必需的参数 -b/--bgenFile 缺失"
    exit 1
fi
if [[ -z "$chain" ]]; then
    echo "必需的参数 -c/--chain 缺失"
    exit 1
fi

if [[ -z "$out" ]]; then
    echo "必需的参数 -o/--out 缺失"
    exit 1
fi

if [[ -z "$threads" ]]; then
    echo "必需的参数 -t/--threads 缺失"
    exit 1
fi

plink2 --bgen ${bgenFile}.bgen ${ref_order} --sample ${bgenFile}.sample --threads ${threads} --make-bed --out ${bgenFile}
rm ${bgenFile}.log
# Step2 bim to genome bed file for liftover
cat ${bgenFile}.bim | mawk '{ print "chr"$1, $4-1, $4, $4, $2 }' | sed 's/^chr23/chrX/' | sed 's/^chr24/chrY/' | sed 's/^chr25/chrX/' | sed 's/^chr26/chrMT/' >${bgenFile}.ZeroBasedPos.bed # $4 -1 是为了构建bed的start 列
# Step3 liftover bed file for [hg19] -> [hg38]
## [opt] 控制输出格式，输出文件名
# unmapped should be exclude at echo how many unmapped

liftOver ${bgenFile}.ZeroBasedPos.bed ${chain} ${bgenFile}.liftOver.bed ${bgenFile}.liftOver.unmapped

## get unmapped variants
mawk <${bgenFile}.liftOver.unmapped '$0~/^#/{next} {print $5}' >${bgenFile}.unmapped_variants
cat ${bgenFile}.unmapped_variants | wc -l | xargs -I{} echo "{} not mapped" # echo unmapped num

## Generate update-pos list for Plink
mawk <${bgenFile}.liftOver.bed '{print $5,$3}' >${bgenFile}.new_pos

## update the new pos
plink2 --bfile ${bgenFile} --exclude ${bgenFile}.unmapped_variants --update-map ${bgenFile}.new_pos --export bgen-1.1 --out ${out} --threads $threads
# Step4 删除中间文件
rm ${bgenFile}.bed ${bgenFile}.bim ${bgenFile}.fam ${bgenFile}.ZeroBasedPos.bed ${bgenFile}.unmapped_variants ${bgenFile}.new_pos
