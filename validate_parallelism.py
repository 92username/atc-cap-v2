#!/usr/bin/env python3
"""
Script de validação das modificações de paralelismo
Verifica se todas as mudanças foram aplicadas corretamente
"""

import os
import sys
from pathlib import Path


def check_file_content(filepath, search_string, description):
    """Verifica se um arquivo contém uma string específica"""
    try:
        with open(filepath, encoding="utf-8") as f:
            content = f.read()
            if search_string in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description}")
                return False
    except FileNotFoundError:
        print(f"❌ {description} - Arquivo não encontrado: {filepath}")
        return False
    except Exception as e:
        print(f"❌ {description} - Erro: {e}")
        return False


def main():
    """Executa validações"""

    print("\n" + "=" * 70)
    print("🔍 VALIDAÇÃO DE PARALELISMO - TATIC PROCESSOR")
    print("=" * 70 + "\n")

    base_path = Path(__file__).parent
    checks = []

    # 1. Verificar app.py
    print("📄 Verificando app.py...")
    checks.append(
        check_file_content(
            base_path / "app.py",
            "from pandarallel import pandarallel",
            "  ├─ Importação de pandarallel",
        )
    )
    checks.append(
        check_file_content(
            base_path / "app.py",
            "pandarallel.initialize(nb_workers=2",
            "  ├─ Inicialização com 2 workers",
        )
    )
    checks.append(
        check_file_content(
            base_path / "app.py",
            'st.success("✅ Processamento paralelo ativado',
            "  └─ Mensagem de status",
        )
    )

    # 2. Verificar tatic_processor.py
    print("\n📄 Verificando tatic_processor.py...")
    checks.append(
        check_file_content(
            base_path / "tatic_processor.py",
            "PARALLEL_ENABLED = True",
            "  ├─ Flag global de paralelismo",
        )
    )
    checks.append(
        check_file_content(
            base_path / "tatic_processor.py",
            "def _apply_parallel(self",
            "  ├─ Método helper _apply_parallel()",
        )
    )
    checks.append(
        check_file_content(
            base_path / "tatic_processor.py",
            'self._apply_parallel(d["pista"], self.normalize_pista)',
            "  ├─ Normalização de pistas paralelizada",
        )
    )
    checks.append(
        check_file_content(
            base_path / "tatic_processor.py",
            'self._apply_parallel(d_rwy["equipamento"], self.get_aircraft_category)',
            "  ├─ Classificação de aeronaves paralelizada",
        )
    )
    checks.append(
        check_file_content(
            base_path / "tatic_processor.py",
            'self._apply_parallel(g, lambda x: f"{x',
            "  ├─ Formatação de datas paralelizada",
        )
    )
    checks.append(
        check_file_content(
            base_path / "tatic_processor.py",
            'self._apply_parallel(d_rwy["weekday"], self.get_weekday_name)',
            "  └─ Obtenção de dias da semana paralelizada",
        )
    )

    # 3. Verificar requirements.txt
    print("\n📄 Verificando requirements.txt...")
    checks.append(
        check_file_content(
            base_path / "requirements.txt",
            "pandarallel>=1.6.5",
            "  └─ Dependência pandarallel adicionada",
        )
    )

    # 4. Verificar documentação
    print("\n📚 Verificando documentação...")
    checks.append(
        check_file_content(
            base_path / "PARALELISMO_PANDARALLEL.md",
            "Implementação de Paralelismo",
            "  ├─ Documento PARALELISMO_PANDARALLEL.md",
        )
    )
    checks.append(
        check_file_content(
            base_path / "PARALELISMO_README.md",
            "Implementação de Paralelismo com Pandarallel",
            "  └─ Documento PARALELISMO_README.md",
        )
    )

    # 5. Verificar scripts
    print("\n📜 Verificando scripts...")
    script_path = base_path / "scripts" / "test_parallelism.sh"
    if script_path.exists():
        print("✅ Script test_parallelism.sh encontrado")
        if os.access(script_path, os.X_OK):
            print("✅ Script é executável")
            checks.append(True)
        else:
            print("⚠️  Script não é executável")
            checks.append(False)
    else:
        print("❌ Script test_parallelism.sh não encontrado")
        checks.append(False)

    # Resumo
    print("\n" + "=" * 70)
    total = len(checks)
    passed = sum(checks)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"📊 RESUMO: {passed}/{total} verificações passaram ({percentage:.1f}%)")

    if all(checks):
        print("✅ TODAS AS MUDANÇAS FORAM APLICADAS COM SUCESSO!")
        print("\n🚀 Próximas etapas:")
        print("   1. pip install -r requirements.txt")
        print("   2. bash scripts/test_parallelism.sh")
        print("   3. streamlit run app.py")
        return 0
    else:
        print("❌ ALGUMAS MUDANÇAS NÃO FORAM APLICADAS CORRETAMENTE!")
        print("\n⚠️  Verifique os itens marcados com ❌ acima")
        return 1


if __name__ == "__main__":
    sys.exit(main())
