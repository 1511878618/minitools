#!/bin/bash
#########################################################
# Function : Conditional Analysis By regenie            #
# Platform : All Linux Based Platform                   #
# Version  : 1.1                                        #
# Date     : 2023-06-13                                 #
# Author   : Tingfeng Xu                                #
# Contact  : xutingfeng@big.ac.cn                       #
#########################################################

usage() {
    cat >&2 <<-EOF
使用方法: $(basename "$0") <option>

可用选项 <option> 包括:
    -p, --pfile <pfile>             plink pfile path, must be specified
    --phenoFile <phenoFile>         pheno file path, must be specified, like:/pmaster/xutingfeng/dataset/ukb/phenotype/regenie_qt.tsv
    --pheno <pheno>                  pheno name, must be specified
    -t, --threads <threads>         threads, default value is 20
    --step1 <step1>                 step1 pred file path, must be specified
    -o, --out <out>                 output prefix, default value is ./conditionalAnalysis
    --exclude-mode <log10p_cutoff>  exclude mode, optional parameter, log10p_cutoff
    --max-condsnp  <value>           max cond snp, default value is 100
    --bt                             bt mode, default is false, and be qt model   

示例:
    $(basename "$0") -p <pfile> --phenoFile <phenoFile> --pheno <pheno> -t <threads> --step1 <step1> -o <out>

    $(basename "$0")  -p /pmaster/xutingfeng/dataset/ukb/dataset/snp/test/SORT_pgen --phenoFile /pmaster/xutingfeng/dataset/ukb/phenotype/regenie_qt.tsv --pheno ldl_a -t 20 --step1 step1/qt_step1_pred.list -o test/test_qt

    parallel run qt: 
    parallel -q echo "sbatch -J '{1}_{2}_regenie' -c 10
    --mem=15G -o log/%j_{1}_{2}.log --wrap '$(basename "$0") -p /pmaster/xutingfeng/dataset/ukb/dataset/snp/wgs/GRCh38/{1} --phenoFile
    /pmaster/xutingfeng/dataset/ukb/phenotype/regenie_qt.tsv --pheno {2} -t 10 --step1 ./step1/qt_step1_pred.list -o ./conditionalNew/{
    1}/{2} --exclude-mode 1 '" ::: APOB PCSK9 LDLR SORT1 ::: ldl_a apob |parallel

    parallel run bt:
    parallel -q echo "sbatch -J '{1}_{2}_regenie' -c 10 --mem=15G -o log/%j_{1}_{2}.log --wrap './condAnalysis.sh -p /pmaster/xutingfeng/dataset/ukb/dataset/snp/wgs/GRCh38/{1} --phenoFile /pmaster/xutingfeng/dataset/ukb/phenotype/regenie_bt.tsv --pheno {2} -t 10 --step1 ./step1/bt_step1_pred.list -o ./conditionalNew/{1}/{2} --bt  --exclude-mode 1 '" ::: APOB PCSK9 LDLR SORT1 ::: cad mi |parallel 
注意:
    1. 所有参数都是必需的，除非另有说明。
    2. 默认参数值已在帮助文档中指定。

EOF
    exit 2
}

# 默认参数值
threads=20
outputPath="./conditionalAnalysis"
maxcount=100
defaultLOG10P=6
defaultFREQ=1e-2
regenie_mode="--qt"
# 定义必需的参数列表
required_params=("pgenPath" "phenoFile" "pheno" "predFile")

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
    -p | --pfile)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --pfile 参数需要提供一个值" >&2
            exit 1
        fi
        pgenPath=$2
        shift 2
        ;;
    --phenoFile)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --phenoFile 参数需要提供一个值" >&2
            exit 1
        fi
        phenoFile=$2
        shift 2
        ;;
    --pheno)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --pheno 参数需要提供一个值" >&2
            exit 1
        fi
        pheno=$2
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
    --step1)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --step1 参数需要提供一个值" >&2
            exit 1
        fi
        predFile=$2
        shift 2
        ;;
    -o | --out)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --out 参数需要提供一个值" >&2
            exit 1
        fi
        outputPath=$2
        shift 2
        ;;
    --exclude-mode)
        exclude_mode=true
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --exclude-mode 参数需要提供一个值" >&2
            exit 1
        fi
        excludeLOG10PCUTOFF=$2
        shift 2
        ;;
    --max-condsnp)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --max-count 参数需要提供一个值" >&2
            exit 1
        fi
        maxcount=$2
        shift 2
        ;;
    --bt)
        regenie_mode="--bt --firth --approx --pThresh 0.01"
        shift
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

# 输出缺少的必需参数并退出
if [ ${#missing_params[@]} -gt 0 ]; then
    echo "缺少必需的参数: ${missing_params[*]}" >&2
    usage
    exit 1
fi

# 打印解析后的参数值
echo "pfile 参数值: $pgenPath"
echo "phenoFile 参数值: $phenoFile"
echo "pheno 参数值: $pheno"
echo "threads 参数值: $threads"
echo "step1 参数值: $predFile"
echo "out 参数值: $outputPath"
echo "regenie flag: $regenie_mode"

if [ "$exclude_mode" = true ]; then
    echo "每一步得到的结果中LOG10P小于${excludeLOG10PCUTOFF}的SNP会被提出来作为下一步的排除"
fi

compare_num() {
    awk -v LOG10P=$1 -v freq=$2 -v defaultLOG10P=${defaultLOG10P} -v defaultFREQ=${defaultFREQ} 'BEGIN{if(LOG10P<defaultLOG10P && freq < defaultFREQ){print "1"}else{print "0"}}'
}

mkdir -p ${outputPath}

# Step1 run regenie step2
step2OutPutFile=${outputPath}/step2
mkdir -p ${step2OutPutFile}

regenie --step 2 \
    --threads=${threads} \
    --ref-first \
    --pgen ${pgenPath} \
    --phenoFile ${phenoFile} \
    --phenoCol ${pheno} \
    ${regenie_mode} \
    --covarFile /pmaster/xutingfeng/dataset/ukb/phenotype/regenie.cov \
    --covarColList genotype_array,inferred_sex,age_visit,PC1,PC2,PC3,PC4,PC5,PC6,PC7,PC8,PC9,PC10,assessment_center,age_squared \
    --catCovarList genotype_array,inferred_sex,assessment_center \
    --maxCatLevels 30 \
    --bsize 1000 \
    --out ${step2OutPutFile}/ \
    --minMAC 1 \
    --pred ${predFile}

currentRegenieOutPut=${step2OutPutFile}/_${pheno}.regenie
gzip ${currentRegenieOutPut}

zcat ${currentRegenieOutPut}.gz | awk 'NR==1{print;next}{print | "sort -k12gr"}' | head | column -t | awk 'NR<=2 {print $3,$6,$12}' >>${outputPath}/total.leading # => 提取全部信息 comming soon

# 更新LOG10P和FREQ  => leading SNP freq >0.1 p < 1e-6 必须是；没有就停止
LOG10P=$(tail -n 1 ${outputPath}/total.leading | awk '{print $3}')
FREQ=$(tail -n 1 ${outputPath}/total.leading | awk '{print $2}')

# 如果exclude_mode open 则提取当前的excludeSNPList
if [ "$exclude_mode" = true ]; then
    excludeSNPList_current=${outputPath}/exclude.snplist
    echo "提取Step2的excludeSNPList(log10p < ${excludeLOG10PCUTOFF})到${excludeSNPList_current}"
    zcat "${currentRegenieOutPut}".gz | awk -v excludeLOG10PCUTOFF="${excludeLOG10PCUTOFF}" 'NR==1{next}$12 <excludeLOG10PCUTOFF {print $3}' >>"${excludeSNPList_current}" #  => 提取对应的最后一次所有的信息  comming soon
fi

count=1
while [ $(compare_num ${LOG10P} ${FREQ}) -eq 0 ] && [ ${count} -le ${maxcount} ]; do # => leading SNP freq >0.1 p < 1e-6 必须是；没有就停止
    # for ((i = 1; i <= ${condSNPNum}; i++)); do
    # Step2.1 提取上一步最显著的SNP以及对应的信息到Total.leading

    currentCondDir=${outputPath}/cond${count}
    mkdir -p ${currentCondDir}
    # 提取当前的leading SNP到目录下
    cp ${outputPath}/total.leading ${currentCondDir}/cond.leading

    # 获取当前cond的snplist;跳过header
    tail -n +2 ${currentCondDir}/cond.leading | awk '{print $1}' >${currentCondDir}/cond.snplist

    # 如果exclude_mode open 则提取当前的excludeSNPList
    if [ "$exclude_mode" = true ]; then
        cp ${excludeSNPList_current} ${currentCondDir}/exclude.snplist
        echo "exclude $(cat ${currentCondDir}/exclude.snplist | wc -l) SNPs in ${count} conditionalAnalysis"

        # Step2.2 conditional analysis
        regenie --step 2 \
            --threads=${threads} \
            --ref-first \
            --pgen ${pgenPath} \
            --phenoFile ${phenoFile} \
            --phenoCol ${pheno} \
            --condition-list ${currentCondDir}/cond.snplist \
            --exclude ${currentCondDir}/exclude.snplist \
            ${regenie_mode} \
            --covarFile /pmaster/xutingfeng/dataset/ukb/phenotype/regenie.cov \
            --covarColList genotype_array,inferred_sex,age_visit,PC1,PC2,PC3,PC4,PC5,PC6,PC7,PC8,PC9,PC10,assessment_center,age_squared \
            --catCovarList genotype_array,inferred_sex,assessment_center \
            --maxCatLevels 30 \
            --bsize 1000 \
            --out ${currentCondDir}/ \
            --minMAC 1 \
            --pred ${predFile}

    else
        # Step2.2 conditional analysis
        regenie --step 2 \
            --threads=${threads} \
            --ref-first \
            --pgen ${pgenPath} \
            --phenoFile ${phenoFile} \
            --phenoCol ${pheno} \
            --condition-list ${currentCondDir}/cond.snplist \
            ${regenie_mode} \
            --covarFile /pmaster/xutingfeng/dataset/ukb/phenotype/regenie.cov \
            --covarColList genotype_array,inferred_sex,age_visit,PC1,PC2,PC3,PC4,PC5,PC6,PC7,PC8,PC9,PC10,assessment_center,age_squared \
            --catCovarList genotype_array,inferred_sex,assessment_center \
            --maxCatLevels 30 \
            --bsize 1000 \
            --out ${currentCondDir}/ \
            --minMAC 1 \
            --pred ${predFile}
    fi

    currentRegenieOutPut=${currentCondDir}/_${pheno}.regenie
    gzip ${currentRegenieOutPut}

    # 更新这一轮的leading SNP到total.leading
    zcat ${currentRegenieOutPut}.gz | awk 'NR==1{print;next}{print | "sort -k12gr"}' | head | column -t | awk 'NR==2 {print $3,$6,$12}' >>${outputPath}/total.leading
    # 更新LOG10P和FREQ => leading SNP freq >0.1 p < 1e-6 必须是；没有就停止
    LOG10P=$(tail -n 1 ${outputPath}/total.leading | awk '{print $3}')
    FREQ=$(tail -n 1 ${outputPath}/total.leading | awk '{print $2}')

    # 如果exclude_mode open 则提取当前的excludeSNPList
    if [ "$exclude_mode" = true ]; then
        excludeSNPList_current=${outputPath}/exclude.snplist
        echo "提取${count}的excludeSNPList(log10p < ${excludeLOG10PCUTOFF})到${excludeSNPList_current}"
        zcat "${currentRegenieOutPut}".gz | awk -v excludeLOG10PCUTOFF="${excludeLOG10PCUTOFF}" 'NR==1{next}$12 <excludeLOG10PCUTOFF {print $3}' >>"${excludeSNPList_current}"
    fi
    # 更新计数器
    count=$((${count} + 1))
done

tail -n +2 ${outputPath}/total.leading | awk '{print $1}' >${outputPath}/total.snplist
echo "Finished! at log10p:${LOG10P} and freq:${FREQ} in ${count} ${outputPath}"
