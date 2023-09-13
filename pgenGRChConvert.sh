#!/bin/bash
#########################################################
# Function : pgen genome version convert                #
# Platform : All Linux Based Platform                   #
# Version  : 1.1                                        #
# Date     : 2023-08-18                                 #
# Author   : Tingfeng Xu                                #
# Contact  : xutingfeng@big.ac.cn                       #
#########################################################

usage() {
    cat <<EOF >&2

请使用: $(basename "$0") <option>

可使用的参数 <option> 包括:
    -p/--pfile <bfile>    plink bfile prefix
    -c/--chain <chain>    liftOver chain file folderPath, will match "{target}To{query}.over.chain.gz" file at this folder 
    -T/--target <target>  target genome version, e.g hg19 
    -Q/--query <query>    query genome version, e.g hg38 
    -m/--memory <memory>  memory, default 4096mb 
    -t/--threads <threads> threads
    -o/--out <out>        output prefix

Example:

pgenGRChConvert.sh -p GRCh38_tmp -c /pmaster/xutingfeng/share/liftover_chain/hg19 -T hg19 -Q hg38 -o convertResult           


 parallel -q echo "sbatch -J 'chr{}' -o 'log/chr{}_convert.log' -c 5 --mem=10G --wrap 'pgenGRChConvert.sh -p ukb_imputed_v3_pgen/ukb_imp_chr{}_v3  -t 5 -o ukb_imputed_v3_GRCh38/ukb_imp_chr{}_v3 -c /pmaster/xutingfeng/share/liftover_chain/hg19/hg19ToHg38.over.chain.gz'" ::: \$(seq 1 22) | parallel

EOF
    exit 2
}

# 默认参数值
memory=4096
threads=10
# 定义必需的参数列表
required_params=("pfile" "chain" "target" "query" "out")

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
    -T | --target)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --target 参数需要提供一个值" >&2
            exit 1
        fi
        target=$2
        shift 2
        ;;
    -Q | --query)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --query 参数需要提供一个值" >&2
            exit 1
        fi
        query=$2
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
    -m | --memory)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --memory 参数需要提供一个值" >&2
            exit 1
        fi
        memory=$2
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

set -e # 报错退出

# 打印解析后的参数值
echo "$(basename "$0")"
echo "  -p/--pfile $pfile"
echo "  -c/--chain $chain"
echo "  -T/--target $target"
echo "  -Q/--query $query"
echo "  -t/--threads $threads"
echo "  -m/--memory $memory"
echo "  -o/--out $out"

echo "----------------------------------------" "start pgen genome version convert" "----------------------------------------"
start_time=$(date +%s)

# step1 pvar genome version convert
echo "----------------------------------------" "change pvar genome version convert" "----------------------------------------"
convertResultFile=${out}.pvar.convert
cat ${pfile}.pvar | versionConvert.py -i 1 2 -c ${target} ${query} ${chain} --no-suffix -k >${convertResultFile}

# exclude #NA which is unmapped
excludeFile=${out}.pvar.exclude
upadteFile=${out}.pvar.update

tail -n +2 ${convertResultFile} | grep "NA" | awk '{print $3}' >${excludeFile}
tail -n +2 ${convertResultFile} | grep -v "NA" | awk '{print $3,$2}' >${upadteFile}
echo "----------------------------------------" "change pvar genome version convert finished" "----------------------------------------"

## update the new pos

# 直接 输出pgen
echo "----------------------------------------" "update raw pfile" "----------------------------------------"
plink2 --pfile ${pfile} --exclude ${excludeFile} --update-map ${upadteFile} --make-pgen --out ${out} --threads $threads
# Step4 删除中间文件

# rm ${convertResultFile} ${excludeFile} ${upadteFile}
echo "如果是gwas分析，请注意是否需要更改你的SNP的ID！比如以GRCh38命名的，是否需要更改为GRCh37命名"
echo "----------------------------------------" "update raw pfile finished" "----------------------------------------"

end_time=$(date +%s) # 获取脚本结束时间的秒数

elapsed_time=$((end_time - start_time)) # 计算运行时间（秒）
echo "Command completed in $elapsed_time seconds."
echo "----------------------------------------" "pgen genome version convert finished" "----------------------------------------"
