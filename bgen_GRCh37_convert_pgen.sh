#!/bin/bash
#########################################################
# Function : bgen_GRCh37_to_GRCh38_pgen                 #
# Platform : All Linux Based Platform                   #
# Version  : 1.1                                        #
# Date     : 2023/08/18                                 #
# Author   : Tingfeng Xu                                #
# Contact  : xutingfeng@big.ac.cn                       #
#########################################################

# 默认线程数
threads=10
memory=4096
required_params=(file output chainFile target query)

# 函数：显示帮助文档并退出
usage() {
    cat >&2 <<-EOF
使用方法: $(basename "$0") <option>

可用选项 <option> 包括:
    -b, --bgen <bgenFilePath>            bgen文件路径
    -o, --output <outputPrefix>      输出文件前缀
    -c/--chain <chain>    liftOver chain file folderPath, will match "{target}To{query}.over.chain.gz" file at this folder 
    -T/--target <target>  target genome version, e.g hg19 
    -Q/--query <query>    query genome version, e.g hg38 
    -t, --thread <threadNumber>      线程数，默认为5
    -m, --memory <memory>            内存 mb, 4096

Example:

EOF
    exit 2
}
while [[ $# -gt 0 ]]; do
    case $1 in
    -b | --bgen)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --bgen 参数需要提供一个值" >&2
            exit 1
        fi
        file="$2"
        echo "$1 $2"
        shift 2
        ;;
    -o | --output)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --output 参数需要提供一个值" >&2
            exit 1
        fi
        output="$2"
        echo "$1 $2"
        shift 2
        ;;
    -c | --chain)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --chain 参数需要提供一个值" >&2
            exit 1
        fi
        chainFile="$2"
        echo "$1 $2"
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
    -t | --thread)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --thread 参数需要提供一个值" >&2
            exit 1
        fi
        threads="$2"
        echo "$1 $2"
        shift 2
        ;;
    -m | --memory)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --memory 参数需要提供一个值" >&2
            exit 1
        fi
        memory="$2"
        echo "$1 $2"
        shift 2
        ;;
    -h | --help)
        usage
        ;;
    *)
        echo "未知选项: $1"
        usage
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

# 输出缺少的必需参数并退出
if [ ${#missing_params[@]} -gt 0 ]; then
    echo "缺少必需的参数: ${missing_params[*]}" >&2
    usage
    exit 1
fi

# 打印参数值
# 打印解析后的参数值
echo "$(basename "$0")"
echo " -b/--bgen: $file"
echo " -o/--output: $output"
echo " -c/--chain: $chainFile"
echo " -T/--target: $target"
echo " -Q/--query: $query"
echo " -t/--thread: $threads"
echo " -m/--memory: $memory"

set -e # 报错退出

echo "----------------------------------------" "bgen_GRCh37_to_GRCh38_pgen" "----------------------------------------"
#
outputFolder=$(dirname ${output})
mkdir -p ${outputFolder}

tmp_pgen_37=${output}_tmp # 临时文件

#bgen => pgen
echo "----------------------------------------" "bgen => pgen" "----------------------------------------"
plink2 --bgen ${file}.bgen ref-first --sample ${file}.sample --make-pgen --threads ${threads} --memory ${memory} --out ${tmp_pgen_37}
echo "----------------------------------------" "bgen => pgen done!" "----------------------------------------"
## to aviod rs566228871 对应多个variants 先重命名ID
cat ${tmp_pgen_37}.pvar | body resetID.py -i 3 1 2 4 5 >${tmp_pgen_37}.tmp.pvar && rm ${tmp_pgen_37}.pvar && mv ${tmp_pgen_37}.tmp.pvar ${tmp_pgen_37}.pvar

#GRCh37 => 38
pgenGRChConvert.sh --pfile ${tmp_pgen_37} -c ${chainFile} -T ${target} -Q ${query} --threads ${threads} --out ${output}
# rm tmp File
rm ${tmp_pgen_37}*
# resetID
cat ${output}.pvar | body resetID.py -i 3 1 2 4 5 >${output}.tmp.pvar && rm ${output}.pvar && mv ${output}.tmp.pvar ${output}.pvar

echo "----------------------------------------" "bgen_GRCh37_to_GRCh38_pgen finished" "----------------------------------------"
