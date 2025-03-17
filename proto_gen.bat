@echo off
echo Compiling .proto files to Python...

REM 确保目标目录存在
if not exist ".\account_server\proto" mkdir ".\account_server\proto"
if not exist ".\sync_server\proto" mkdir ".\sync_server\proto"

REM 确保目标目录中有__init__.py文件
echo. > ".\account_server\proto\__init__.py"
echo. > ".\sync_server\proto\__init__.py"

REM 编译所有.proto文件到两个目标目录
for %%f in (.\movan_protobuf\*.proto) do (
    echo Compiling %%f...
    .\movan_protobuf\protoc.exe -I=.\movan_protobuf --python_out=.\account_server\proto %%f
    .\movan_protobuf\protoc.exe -I=.\movan_protobuf --python_out=.\sync_server\proto %%f
)

echo Compilation completed successfully!