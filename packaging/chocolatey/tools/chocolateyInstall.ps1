$ErrorActionPreference = 'Stop'

if (Get-OSArchitectureWidth -Compare 32) {
    throw 'Lingose 0.2.0 provides a Windows x64 executable only.'
}
if ($env:chocolateyForceX86 -eq 'true') {
    throw 'Lingose 0.2.0 does not provide an x86 executable.'
}

$packageArgs = @{
    PackageName    = 'lingose'
    UnzipLocation  = $PSScriptRoot
    Url64bit       = 'https://github.com/englishword/lingose-rust/releases/download/v0.2.0/lingose-v0.2.0-windows-x86_64.zip'
    Checksum64     = 'bf3d61609208c721d7e84b6ed44c91256385080c04ca6c7823f35e256a57b474'
    ChecksumType64 = 'sha256'
}
Install-ChocolateyZipPackage @packageArgs
# Chocolatey automatically creates/removes the shim for the downloaded .exe.
# Preserve the full archive, including the project and third-party notices.
