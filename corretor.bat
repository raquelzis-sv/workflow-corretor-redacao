@echo off
rem Wrapper batch to invoke the Correção de Redação workflowem Usage: corretor <redacao_path> <tema_path_or_text>
if "%~2"=="" (
    echo [ERROR] Dois argumentos são necessários: <caminho_redacao> <caminho_tema_ou_texto>
    exit /b 1
)
python -m scripts.corretor_cli "%~1" "%~2"
if errorlevel 1 (
    echo [ERROR] Execução do workflow falhou.
    exit /b 1
) else (
    echo [OK] Workflow concluído com sucesso.
)
