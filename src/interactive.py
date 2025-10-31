"""
Interface interativa para escolha de modo de ingestão.

Permite ao usuário escolher entre ingestão incremental ou completa.
"""

import logging
from pathlib import Path
from typing import Set, Literal

logger = logging.getLogger(__name__)

IngestionMode = Literal["incremental", "full", "cancel"]


def show_changes_summary(
    new_files: Set[Path],
    modified_files: Set[Path],
    deleted_files: Set[Path],
    indexed_files: Set[Path],
    current_files: Set[Path]
) -> None:
    """
    Exibe resumo de mudanças detectadas.
    
    Args:
        new_files: Arquivos novos
        modified_files: Arquivos modificados
        deleted_files: Arquivos deletados
        indexed_files: Arquivos já indexados
        current_files: Arquivos atuais
    """
    print()
    print("=" * 70)
    print("📊 RESUMO DE MUDANÇAS")
    print("=" * 70)
    print()
    
    print(f"Arquivos já indexados: {len(indexed_files)}")
    print(f"Arquivos atuais: {len(current_files)}")
    print()
    
    print(f"✨ Novos: {len(new_files)}")
    print(f"✏️  Modificados: {len(modified_files)}")
    print(f"🗑️  Deletados: {len(deleted_files)}")
    print()
    
    total_changes = len(new_files) + len(modified_files) + len(deleted_files)
    print(f"📝 Total de mudanças: {total_changes}")
    print()
    
    # Mostrar detalhes (até 5 de cada tipo)
    if new_files:
        print("Novos arquivos:")
        for i, file_path in enumerate(sorted(new_files), 1):
            if i > 5:
                remaining = len(new_files) - 5
                print(f"  ... e mais {remaining} arquivo(s)")
                break
            # Mostrar path relativo se possível
            try:
                rel_path = file_path.relative_to(Path.cwd())
                print(f"  ✨ {rel_path}")
            except ValueError:
                print(f"  ✨ {file_path.name}")
        print()
    
    if modified_files:
        print("Arquivos modificados:")
        for i, file_path in enumerate(sorted(modified_files), 1):
            if i > 5:
                remaining = len(modified_files) - 5
                print(f"  ... e mais {remaining} arquivo(s)")
                break
            try:
                rel_path = file_path.relative_to(Path.cwd())
                print(f"  ✏️  {rel_path}")
            except ValueError:
                print(f"  ✏️  {file_path.name}")
        print()
    
    if deleted_files:
        print("Arquivos deletados:")
        for i, file_path in enumerate(sorted(deleted_files), 1):
            if i > 5:
                remaining = len(deleted_files) - 5
                print(f"  ... e mais {remaining} arquivo(s)")
                break
            try:
                rel_path = file_path.relative_to(Path.cwd())
                print(f"  🗑️  {rel_path}")
            except ValueError:
                print(f"  🗑️  {file_path.name}")
        print()


def prompt_ingestion_mode(
    new_files: Set[Path],
    has_history: bool
) -> IngestionMode:
    """
    Pergunta ao usuário qual modo de ingestão usar.
    
    Args:
        new_files: Arquivos novos detectados
        has_history: Se existe histórico
    
    Returns:
        Modo escolhido: "incremental", "full", ou "cancel"
    """
    print("=" * 70)
    print("MODO DE INGESTÃO")
    print("=" * 70)
    print()
    
    # Se não há histórico, só pode ser full
    if not has_history:
        print("Primeira execução detectada.")
        print("Será realizada ingestão completa de todos os arquivos.")
        print()
        input("Pressione Enter para continuar...")
        return "full"
    
    # Se não há novos arquivos
    if not new_files:
        print("Nenhum arquivo novo detectado.")
        print()
        print("Opções:")
        print("  [1] Cancelar (nada a fazer)")
        print("  [2] Reindexar tudo (ingestão completa)")
        print()
        
        while True:
            choice = input("Escolha (1-2) [padrão: 1]: ").strip() or "1"
            
            if choice == "1":
                return "cancel"
            elif choice == "2":
                return "full"
            else:
                print("❌ Opção inválida. Digite 1 ou 2.")
    
    # Há novos arquivos
    else:
        print("Opções:")
        print(f"  [1] Incremental - Indexar apenas novos arquivos ({len(new_files)} arquivo(s))")
        print("  [2] Completa - Reindexar tudo")
        print("  [3] Cancelar")
        print()
        
        while True:
            choice = input("Escolha (1-3) [padrão: 1]: ").strip() or "1"
            
            if choice == "1":
                return "incremental"
            elif choice == "2":
                return "full"
            elif choice == "3":
                return "cancel"
            else:
                print("❌ Opção inválida. Digite 1, 2 ou 3.")


def confirm_action(message: str, default: bool = True) -> bool:
    """
    Pede confirmação do usuário.
    
    Args:
        message: Mensagem a exibir
        default: Valor padrão (True = Sim, False = Não)
    
    Returns:
        True se confirmado
    """
    default_str = "S/n" if default else "s/N"
    response = input(f"{message} ({default_str}): ").strip().lower()
    
    if not response:
        return default
    
    return response in ('s', 'sim', 'y', 'yes')
