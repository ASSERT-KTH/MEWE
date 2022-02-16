PROGRAM=$1

DEBUG_INFO=$($WASM2WAT -v $PROGRAM -o $PROGRAM.wat 2>&1)

#typeSectionSize=$(echo "$DEBUG_INFO" | grep "BeginTypeSection")
#importSectionSize=$(echo "$DEBUG_INFO" | grep "BeginImportSection")
#functionSectionSize=$(echo "$DEBUG_INFO" | grep "BeginFunctionSection")
#totalFunctions=$(echo "$DEBUG_INFO" | grep "OnFunctionCount")
#tableSectionSize=$(echo "$DEBUG_INFO" | grep "BeginTableSection")
#memorySectionSize=$(echo "$DEBUG_INFO" | grep "BeginMemorySection")
#globalSectionSize=$(echo "$DEBUG_INFO" | grep "BeginGlobalSection")
#exportSectionSize=$(echo "$DEBUG_INFO" | grep "BeginExportSection")
codeSectionSize=$(echo "$DEBUG_INFO" | grep "BeginCodeSection")

# counting exported functions
#exportedFunctionCounts=$(echo "$DEBUG_INFO" | grep -E "OnExport\(index: \d+, kind: func,")

#echo "$exportedFunctionCounts"

echo $codeSectionSize # $typeSectionSize $importSectionSize $functionSectionSize $totalFunctions $tableSectionSize $memorySectionSize $globalSectionSize $exportSectionSize