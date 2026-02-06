param (
    [Parameter(Mandatory=$true)][string]$Prefix,
    [Parameter(Mandatory=$true)][string]$FeatureName
)

$BaseName = "$Prefix$FeatureName"
$Controller = "${BaseName}Controller"
$Service = "${BaseName}Service"
$Contract = "${BaseName}Contract"

Write-Host "🏗️  Scaffolding SysOperation Framework for: $FeatureName"
Write-Host "Prefix: $Prefix"

$ControllerCode = @"
[SysOperationJournaledParametersAttribute(true)]
class $Controller extends SysOperationServiceController
{
    public static void main(Args _args)
    {
        $Controller controller;
        controller = new $Controller();
        controller.parmClassName(classStr($Service));
        controller.parmMethodName(methodStr($Service, process));
        controller.startOperation();
    }
}
"@

$ServiceCode = @"
class $Service
{
    public void process($Contract _contract)
    {
        // Implementation goes here
        Info(strFmt("Processing %1...", _contract.parmId()));
    }
}
"@

$ContractCode = @"
[DataContractAttribute]
class $Contract
{
    str id;

    [DataMemberAttribute, SysOperationLabelAttribute(literalStr("ID")), SysOperationHelpTextAttribute(literalStr("Identifier"))]
    public str parmId(str _id = id)
    {
        id = _id;
        return id;
    }
}
"@

# Output files (simulated here by printing, or writing to current dir)
$ControllerCode | Out-File -Encoding UTF8 "${Controller}.xml"
$ServiceCode | Out-File -Encoding UTF8 "${Service}.xml"
$ContractCode | Out-File -Encoding UTF8 "${Contract}.xml"

Write-Host "✅ Generated 3 class files in current directory."
Write-Host "   - ${Controller}.xml"
Write-Host "   - ${Service}.xml"
Write-Host "   - ${Contract}.xml"
