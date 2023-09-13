#!/bin/bash
#########################################################
# Function : Conditional Analysis By regenie            #
# Platform : All Linux Based Platform                   #
# Version  : 1.1                                        #
# Date     : 2023-06-13                                 #
# Author   : Tingfeng Xu                                #
# Contact  : xutingfeng@big.ac.cn                       #
#########################################################

# 默认线程数
threadNumber=20
required_params=(wesFilePath imputationFilePath outputPrefix)

alias bcftools='/usr/local/bin/bcftools'
# 函数：显示帮助文档并退出
usage() {
    cat >&2 <<-EOF
使用方法: $(basename "$0") <option>

可用选项 <option> 包括:
    -w, --wes <wesFilePath>            WES文件路径
    -i, --imputation <imputationFilePath>  Imputation文件路径
    -o, --output <outputPrefix>      输出文件前缀
    -t, --thread <threadNumber>      线程数，默认为20
    -h, --help                       显示帮助文档并退出

Example:
mergeWES_IMPUTATION.sh -w /srv/xutingfeng/dataset/ukb/dataset/snp/WES_IMPUTATION/WES/update/PCSK9 -i /srv/xutingfeng/dataset/ukb/dataset/snp/WES_IMPUTATION/IMPUTATION/GRCh38/PCSK9 -o PCSK9_imp_wes  -t 30

parallel -q echo "sbatch -J '{}' -c 30 --mem=50G -x node1 -o '%j_{}.sbatch.out'  ./mergeWES_IMPUTATION.sh -w /srv/xutingfeng/dataset/ukb/dataset/snp/WES_IMPUTATION/WES/update/{} -i /srv/xutingfeng/dataset/ukb/dataset/snp/WES_IMPUTATION/IMPUTATION/GRCh38/{} -o {}_imp_wes  -t 30" ::: APOB PCSK9 LDLR SORT1 | head

EOF
    exit 2
}

# 处理命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
    -w | --wes)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --wes 参数需要提供一个值" >&2
            exit 1
        fi
        wesFilePath="$2"
        echo "$1 $2"
        shift 2
        ;;
    -i | --imputation)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --imputation 参数需要提供一个值" >&2
            exit 1
        fi
        imputationFilePath="$2"
        echo "$1 $2"
        shift 2
        ;;
    -o | --output)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --output 参数需要提供一个值" >&2
            exit 1
        fi
        outputPrefix="$2"
        echo "$1 $2"
        shift 2
        ;;
    -t | --thread)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --thread 参数需要提供一个值" >&2
            exit 1
        fi
        threadNumber="$2"
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
echo "WES文件路径: $wesFilePath"
echo "Imputation文件路径: $imputationFilePath"
echo "输出文件前缀: $outputPrefix"
echo "线程数: $threadNumber"

set -e # 报错退出
# step1 从IMPUTATION中排除WES的部分SNP

tmpWESSNPList=${outputPrefix}.tmp.wes.snplist
cat ${wesFilePath}.pvar | awk 'NR==1{next}{print $3}' >${tmpWESSNPList}

beforeExclude=$(cat ${imputationFilePath}.pvar | wc -l)
tmpIMPUTATIONExcludeWESSNP=${outputPrefix}.tmp.imputation_excludeWES
tmpWES=${outputPrefix}.tmp.wes
# remove sample
echo "提取WES和IMPUTATION的交集"

keepID=${outputPrefix}.tmp.keepID
#### 提取交集
comm -12 <(tail -n +2 ${imputationFilePath}.psam | sort) <(tail -n +2 ${wesFilePath}.psam | sort) | awk 'NR==1{print "#FID", "IID"}NR>=2{print $1, $1}' | body sort -k1n >${keepID}
#### 目前由于plink2只支持concatenate，所以只能先提取交集，然后再排除WES部分SNP => 以后可以修改，减少计算量
###### 排除IMPUTATION中的WES部分SNP；并且提取WES和IMPUTATION中的交集sample
plink2 --pfile ${imputationFilePath} --exclude ${tmpWESSNPList} --keep ${keepID} --make-pgen --out ${tmpIMPUTATIONExcludeWESSNP} --threads ${threadNumber} --indiv-sort n --sort-vars n >/dev/null

######  提取WES中的交集sample，
plink2 --pfile ${wesFilePath} --keep ${keepID} --make-pgen --out ${tmpWES} --threads ${threadNumber} --indiv-sort n --sort-vars n >/dev/null
#### 输出SNP的变化情况
afterExclude=$(cat ${tmpIMPUTATIONExcludeWESSNP}.pvar | wc -l)
wesSNPCount=$(cat ${wesFilePath}.pvar | wc -l)

echo "WES数据的SNP数目为：${wesSNPCount}"
echo "IMPUTATION有SNP${beforeExclude}"
echo "与WES存在重合数目为：$((${beforeExclude} - ${afterExclude}))"
echo "排除这部分后IMP数据的SNP数目为：${afterExclude}"

#### 输出sample变化情况
echo "WES有$(tail -n +2 ${wesFilePath}.psam | wc -l)个样本"
echo "imputation有$(tail -n +2 ${imputationFilePath}.psam | wc -l)个样本"
echo "WES 和 IMPUTATION的交集有$(tail -n +2 ${keepID} | wc -l)个样本"
echo "WES用于合并的有$(tail -n +2 ${tmpWES}.psam | wc -l)个样本"
echo "IMPUTATION用于合并的有$(tail -n +2 ${tmpIMPUTATIONExcludeWESSNP}.psam | wc -l)个样本"

# step2 合并WES和排除WES部分后的IMPUTATION的数据
echo "---------------------------------concatenate---------------------------------"
echo "开始合并................."
plink2 --pfile ${tmpWES} --export bcf --out ${tmpWES} --threads ${threadNumber} >/dev/null
plink2 --pfile ${tmpIMPUTATIONExcludeWESSNP} --export bcf --out ${tmpIMPUTATIONExcludeWESSNP} --threads ${threadNumber} >/dev/null

bcftools concat ${tmpWES}.bcf ${tmpIMPUTATIONExcludeWESSNP}.bcf -o ${outputPrefix}.tmp.merge.bcf -O b --threads ${threadNumber} >/dev/null

plink2 --bcf ${outputPrefix}.tmp.merge.bcf --make-pgen --out ${outputPrefix} --threads ${threadNumber} --id-delim --psam ${tmpWES}.psam
rm ${outputPrefix}.tmp.*
# rm
# mergeList=${outputPrefix}.tmp.mergelist
# echo -e "${tmpWES}\n${tmpIMPUTATIONExcludeWESSNP}" >${mergeList}
# plink2 --pmerge-list ${mergeList} --make-pgen --out ${outputPrefix} --threads ${threadNumber}

# echo "successful merge data!!!!!"
# plink2
