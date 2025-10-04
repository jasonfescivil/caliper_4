$ids=@("344b98a7-f9ff-4e8e-83c7-128f6ecdd5a4","742e122c-3551-4187-9a9e-0ead017c019f",
"03f712a9-68d1-42ba-9dcf-499ae5ec24aa","747cbce6-035d-461a-8b95-df6dafadcfc2",
"b45e47a4-c2ae-4812-b8ab-e01f3c946855","40769edc-dd33-4ec8-b148-e631865e163e")
$h=@{Authorization="Bearer $env:LLAMA_CLOUD_API_KEY"}
foreach($pipelineId in $ids){
  $r=Invoke-RestMethod -Headers $h -Uri "https://api.cloud.llamaindex.ai/api/v1/pipelines/$pipelineId" -Method Get
  "{0}  {1}  {2}" -f $pipelineId, $r.embedding_config.type, $r.embedding_config.component.model_name
}