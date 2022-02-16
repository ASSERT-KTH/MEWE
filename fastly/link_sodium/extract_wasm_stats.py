import sys
import re
from subprocess import check_output
import json
import subprocess
import os

# regular expressions to match meta
TYPE_SECTION_SIZE=re.compile(r"BeginTypeSection\((\d+)\)")
IMPORT_SECTION_SIZE=re.compile(r"BeginImportSection\((\d+)\)")
FUNCTION_SECTION_SIZE=re.compile(r"BeginFunctionSection\((\d+)\)")
FUNCTION_COUNT=re.compile(r"OnFunctionCount\((\d+)\)")
TABLE_SECTION_SIZE=re.compile(r"BeginTableSection\((\d+)\)")
MEMORY_SECTION_SIZE=re.compile(r"BeginMemorySection\((\d+)\)")
GLOBAL_SECTION_SIZE=re.compile(r"BeginGlobalSection\((\d+)\)")
EXPORT_SECTION_SIZE=re.compile(r"BeginExportSection\((\d+)\)")

ELEMENT_SECTION_SIZE=re.compile(r"BeginElemSection\((\d+)\)")
CODE_SECTION_SIZE=re.compile(r"BeginCodeSection\((\d+)\)")
DATA_SECTION_SIZE=re.compile(r"BeginDataSection\((\d+)\)")
CUSTOM_SECTIONS=re.compile(r"BeginCustomSection\(\"(.*?)\", size: (\d+)\)")

def extractSize(meta, r):
    return int(r.search(meta).group(1))

def extract_exported_function_names(meta):
    export_re = re.compile(r"OnExport\(index: (\d+), kind: func, item_index: \d+, name: \"(.*?)\"")

    result = []
    for m in export_re.finditer(meta):
        result.append((m.group(1), m.group(2)))

    return result

def process(wasmbinary):
    # call wasm2wat with verbose to extract metadata
    meta = check_output(
        [
            os.getenv("WASM2WAT"),
            "-v",
            wasmbinary,
            "-o",
            "/dev/null"
        ],
        stderr=subprocess.DEVNULL
    )
    meta = meta.decode()
    typSize = extractSize(meta, TYPE_SECTION_SIZE)
    impSize = extractSize(meta, IMPORT_SECTION_SIZE)
    funcSize = extractSize(meta, FUNCTION_SECTION_SIZE)
    funcCount = extractSize(meta, FUNCTION_COUNT)
    exportSize = extractSize(meta, EXPORT_SECTION_SIZE)
    globalSize = extractSize(meta, GLOBAL_SECTION_SIZE)
    memSize = extractSize(meta, MEMORY_SECTION_SIZE)
    tableSize = extractSize(meta, TABLE_SECTION_SIZE)

    functions = extract_exported_function_names(meta)

    elemSize = extractSize(meta, ELEMENT_SECTION_SIZE)
    codeSize = extractSize(meta, CODE_SECTION_SIZE)
    dataSize = extractSize(meta, DATA_SECTION_SIZE)

    print(typSize, impSize, funcSize, funcCount, exportSize, globalSize, memSize, tableSize)
    print(functions)
    print(elemSize, codeSize, dataSize)

    # TODO, extract full custom sections

    # Return dict for saving
    return dict(
        type_section_size=typSize,
        code_section_size=codeSize,
        function_section_size=funcSize,
        exported_function_names=functions,
        element_section_size=elemSize,
        data_section_size=dataSize,
        global_section_size=globalSize,
        memory_section_size=memSize,
        table_section_size=tableSize,
        import_section_size=impSize
    )
if __name__ == '__main__':
    process(sys.argv[1])