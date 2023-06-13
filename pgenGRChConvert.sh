#!/bin/bash
#########################################################
# Function : pgen genome version convert                #
# Platform : All Linux Based Platform                   #
# Version  : 1.0                                        #
# Date     : 2023-06-02                                 #
# Author   : Tingfeng Xu                                #
# Contact  : xutingfeng@big.ac.cn                       #
#########################################################

usage() {
    cat <<EOF >&2

请使用: $(basename "$0") <option>

可使用的参数 <option> 包括:
    -p/--pfile <bfile>    plink bfile prefix
    -c/--chain <chain>    liftOver chain file
    -t/--threads <threads> threads
    -o/--out <out>        output prefix

EOF
    exit 2
}

# 默认参数值

# 定义必需的参数列表
required_params=("pfile" "chain" "out" "threads")

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
    -p | --pfile)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --pfile 参数需要提供一个值" >&2
            exit 1
        fi
        pfile=$2
        shift 2
        ;;
    -c | --chain)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --chain 参数需要提供一个值" >&2
            exit 1
        fi
        chain=$2
        shift 2
        ;;
    -t | --threads)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --threads 参数需要提供一个值" >&2
            exit 1
        fi
        threads=$2
        shift 2
        ;;
    -o | --out)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --out 参数需要提供一个值" >&2
            exit 1
        fi
        out=$2
        shift 2
        ;;
    -h | --help)
        usage
        ;;
    *)
        echo "未知选项: $key" >&2
        usage
        exit 1
        ;;
    esac
done

# 检查必需的参数是否提供
missing_params=()
for param in "${required_params[@]}"; do
    if [ -z "${!param}" ]; then
        missing_params+=("$param")
    fi
done

# 输出缺少的必需参数并报错
if [ ${#missing_params[@]} -gt 0 ]; then
    echo "缺少必需的参数: ${missing_params[*]}" >&2
    usage
    exit 1
fi

# 打印解析后的参数值
echo "$(basename "$0")"
echo "  -p/--pfile $pfile"
echo "  -c/--chain $chain"
echo "  -t/--threads $threads"
echo "  -o/--out $out"

# plink2 --bgen ${pfile}.bgen ${ref_order} --sample ${pfile}.sample --threads ${threads} --make-pgen --out ${pfile}.tmp
# rm ${pfile}.log
# Step2 bim to genome bed file for liftover
cat ${pfile}.pvar | mawk 'NR==1 {next}{ print "chr"$1, $2-1, $2, $2, $3 }' | sed 's/^chr23/chrX/' | sed 's/^chr24/chrY/' | sed 's/^chr25/chrX/' | sed 's/^chr26/chrMT/' >${pfile}.tmp.ZeroBasedPos.bed # $2 -1 是为了构建bed的start 列
# Step3 liftover bed file for [hg19] -> [hg38]
## [opt] 控制输出格式，输出文件名
# unmapped should be exclude at echo how many unmapped

liftOver ${pfile}.tmp.ZeroBasedPos.bed ${chain} ${pfile}.liftOver.bed ${pfile}.liftOver.unmapped

## get unmapped variants
mawk <${pfile}.liftOver.unmapped '$0~/^#/{next} {print $5}' >${pfile}.unmapped_variants
cat ${pfile}.unmapped_variants | wc -l | xargs -I{} echo "{} not mapped" # echo unmapped num

## Generate update-pos list for Plink
mawk <${pfile}.liftOver.bed '{print $5,$3}' >${pfile}.new_pos

## update the new pos

# if [[ "$export" == "bed" ]]; then
#     plink2 --pfile ${pfile} --exclude ${pfile}.unmapped_variants --update-map ${pfile}.new_pos --make-bed --out ${out} --threads $threads
# elif [[ "$export" == "pgen" ]]; then
#     plink2 --pfile ${pfile} --exclude ${pfile}.unmapped_variants --update-map ${pfile}.new_pos --make-pgen --out ${out} --threads $threads
# else
#     # 当变量 a 的值不为 "bed" 时执行的代码块
#     plink2 --pfile ${pfile} --exclude ${pfile}.unmapped_variants --update-map ${pfile}.new_pos --export ${export} --out ${out} --threads $threads
# fi
# 直接 输出pgen
plink2 --pfile ${pfile} --exclude ${pfile}.unmapped_variants --update-map ${pfile}.new_pos --make-pgen --out ${out} --threads $threads
# Step4 删除中间文件
rm ${pfile}.tmp.*

echo "如果是gwas分析，请注意是否需要更改你的SNP的ID！比如以GRCh38命名的，是否需要更改为GRCh37命名"
