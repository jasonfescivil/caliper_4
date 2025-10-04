#!/bin/bash
# Monitor indexing progress

echo "📊 Monitoring Caliper Indexing Progress"
echo "======================================"

# Check how many PDFs to process
echo -e "\n📁 Total PDFs to process:"
find knowledge_base -name "*.pdf" -type f | wc -l

echo -e "\n📂 PDFs per directory:"
for dir in knowledge_base/*/; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -name "*.pdf" -type f | wc -l)
        if [ $count -gt 0 ]; then
            echo "  $(basename "$dir"): $count PDFs"
        fi
    fi
done

echo -e "\n💾 Index progress (updated every 10 seconds):"
echo "Press Ctrl+C to stop monitoring"
echo ""

while true; do
    # Check index directory size
    if [ -d "data_v2/indexes/all_docs_enhanced" ]; then
        size=$(du -sh data_v2/indexes/all_docs_enhanced 2>/dev/null | cut -f1)
        files=$(find data_v2/indexes/all_docs_enhanced -type f | wc -l)
        echo -ne "\r🔄 Index size: $size | Files: $files | $(date '+%H:%M:%S')    "
    else
        echo -ne "\r⏳ Waiting for index creation... $(date '+%H:%M:%S')    "
    fi
    sleep 10
done
