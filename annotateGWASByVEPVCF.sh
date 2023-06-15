#!/bin/bash
#########################################################
# Function :pgen genome version convert                 #
# Platform :All Linux Based Platform                    #
# Version  :1.0                                         #
# Date     :2023-06-02                                  #
# Author   :Tingfeng Xu                                 #
# Contact  :xutingfeng@big.ac.cn                        #
#########################################################
usage() {
    cat <<-EOF >&2
使用方法: $(basename "$0") <option>

可用选项 <option> 包括:
    -i, --file <file>    输入文件; should have header
    -C, --col <snpCol> <pvalueCol>    SNP ID 列和 [pvalue|-log10P] 列，格式如：1 2
    -o, --out <out>    输出前缀
    -v, --vcf <vcf>    VCF 文件；[vcf|vcf.gz]；目前只适合于VEP注释的VCF文件
    -c, --cutoff <cutoff>    阈值；默认值为LOG10P为 8；请谨慎选择，确保数据是 -log10P 还是 P；用于对input file 进行过滤

示例:
    $(basename "$0") -i <input_file> -C <snpCol> <pvalueCol> -o <output_prefix> -v <vcf_file> -c <cutoff>

    $(basename "$0") -i total.leading --col 1 3 -v /srv/zhangrufa[0/1872]re_variants/annotation/vep/chr2_vep_output.vcf.gz -c 8 -o tmp

    如 --file total.leading, total.leading looks like below:
    -------------------------------------------------------
    ID A1FREQ LOG10P
    2:21043902:GGCAGCGCCA:G 0.329025 296.568
    2:21068657:G:A 0.814297 158.375
    -------------------------------------------------------
    so will merge VCF by ID and filter by LOG10P > '-c 8' 
    by: --col 1 3 指定ID是第一列，LOG10P是第三列
    by: --vcf /srv/zhangrufa[0/1872]re_variants/annotation/vep/chr2_vep_output.vcf.gz 指定vcf file
    by: --cutoff 8 指定保留大于8的LOG10P的SNP
    by: --out tmp 指定输出前缀
    -------------------------------------------------------
    output file: tmp.merge, tmp.log
    tmp.merge like below:
    -------------------------------------------------------
    ID A1FREQ LOG10P Allele Consequence IMPACT SYMBOL Gene Feature_type Feature BIOTYPE EXON INTRON HGVSc HGVSp cDNA_position CDS_position Protein_position Amino_acids Codons Existing_variation DISTANCE STRAND FLAGS SYMBOL_SOURCE HGNC_ID
    2:20297508:A:G 2.63509e-06 18.6885 G intron_variant MODIFIER PUM2 ENSG00000055917 Transcript ENST00000338086 protein_coding NA 7/19 NA NA NA NA NA NA NA NA NA -1 NA HGNC HGNC:14958
    2:20297508:A:G 2.63509e-06 18.6885 G intron_variant MODIFIER PUM2 ENSG00000055917 Transcript ENST00000361078 protein_coding NA 8/20 NA NA NA NA NA NA NA NA NA -1 NA HGNC HGNC:14958

注意:
    1. 所有参数都是必需的，除非另有说明。
    2. 请在使用前确保正确理解参数的含义和使用方法。

EOF
    exit 2
}
# 默认参数值
cutoff=8

# 定义必需的参数列表
required_params=("input_file" "snp_col" "output_prefix" "vcf_file")

# 解析命令行参数
echo "$(basename "$0")"

while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
    -i | --file)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --file 参数需要提供一个值" >&2
            exit 1
        fi
        input_file="$2"
        echo "$1 $2"
        shift 2
        ;;
    -C | --col)

        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --col 参数至少需要一个值" >&2
            exit 1
        fi
        snp_col="$2"

        if [[ -z "$3" || "$3" == -* ]]; then
            echo "$1 $2"

            shift 2
        else
            echo "$1 $2 $3"
            pvalue_col="$3"
            sfhit 3
        fi
        ;;
    -o | --out)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --out 参数需要提供一个值" >&2
            exit 1
        fi
        output_prefix="$2"
        echo "$1 $2"
        shift 2
        ;;
    -v | --vcf)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --vcf 参数需要提供一个值" >&2
            exit 1
        fi
        vcf_file="$2"
        echo "$1 $2"
        shift 2
        ;;
    -c | --cutoff)
        if [[ -z "$2" || "$2" == -* ]]; then
            echo "错误: --cutoff 参数需要提供一个值" >&2
            exit 1
        fi
        cutoff="$2"
        echo "$1 $2"
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

# 输出缺少的必需参数
if [ ${#missing_params[@]} -gt 0 ]; then
    echo "缺少必需的参数: ${missing_params[*]}" >&2
    usage
    exit 1
fi

# 打印解析后的参数值
# echo "-i/--input: $input_file"
# echo "-C/--col: $snp_col $pvalue_col"
# echo "-o/--out: $output_prefix"
# echo "-v/--vcf: $vcf_file"
# echo "-c/--cutoff: $cutoff"

# extract log10P = >8 >annotate_tmp.pos
posFile=${output_prefix}.tmp.pos
filterInputFile=${output_prefix}.filter
if [[ "${input_file##*.}" == "gz" ]]; then
    zcat ${input_file} | snpID2bed.py -i ${snp_col} --no-chr | awk -v cutoff=${cutoff} -v p_col=${pvalue_col} 'NR==1{print;next}{if($(p_col+5) > cutoff){print}}' >${filterInputFile}

else
    cat ${input_file} | snpID2bed.py -i ${snp_col} --no-chr | awk -v cutoff=${cutoff} -v p_col=${pvalue_col} 'NR==1{print;next}{if($(p_col+5) > cutoff){print}}' >${filterInputFile}
fi

cat ${filterInputFile} | awk '{print $1,$2}' >${posFile}

cat ${filterInputFile} | wcut -f6--1 >${filterInputFile}.tmp
rm ${filterInputFile} && mv ${filterInputFile}.tmp ${filterInputFile}

# vep extract => vcf file , this file will keep
vcfExtract=${output_prefix}

if [[ "${vcf_file##*.}" == "gz" ]]; then
    vcftools --gzvcf ${vcf_file} --positions ${posFile} --recode --recode-INFO-all --out ${vcfExtract}
else
    vcftools --vcf ${vcf_file} --positions ${posFile} --recode --recode-INFO-all --out ${vcfExtract}
fi

#vcf clean file: snpID, info
vcfCleanFile=${output_prefix}.vep

# 这个地方ParseVEPAnnotation4VCF专门解析VEP的VCF，如果是其他的要合并，这里需要修改
# VEP 的前五列分别是：CHROM POS ID REF ALT => resetID.py => ID 变成：CHROM:POS:REF:ALT，进行后续匹配 => wcut -f 3,6--1 保留 ID(第三列)和ParseVEPAnnotation4VCF.py 生成的 INFO(第六列及之后)的结果，wcut可以换成awk的for循环
cat ${vcfExtract}.recode.vcf | ParseVEPAnnotation4VCF.py | resetID.py -i 3 1 2 4 5 -c "#" | wcut -f 3,6--1 >${vcfCleanFile}

#merge regenie with vcf exract file
merge.py -l ${filterInputFile} -r ${vcfCleanFile} -o "${snp_col};1" --how "inner" >${output_prefix}.merge

rm ${output_prefix}.tmp.*
rm ${vcfExtract}.recode.vcf
rm ${output_prefix}.log
rm ${filterInputFile} ${vcfCleanFile}
