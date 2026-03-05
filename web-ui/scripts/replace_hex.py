
files = [
    '/home/jefersonlopes/Developer/local-repositories/sovereign-pair/web-ui/src/components/Vault/BlockEditor.vue',
    '/home/jefersonlopes/Developer/local-repositories/sovereign-pair/web-ui/src/views/VaultView.vue'
]

replacements = {
    'bg-[#0E0E10]': 'bg-surface-900',
    'bg-[#121214]': 'bg-surface-800',
    'bg-[#18181B]': 'bg-surface-800',
    'bg-[#1E1E20]': 'bg-surface-700',
    'border-[#222]': 'border-surface-700',
    'border-[#222222]': 'border-surface-700',
    'text-[#E0E0E0]': 'text-surface-200',
    'text-zinc-200': 'text-surface-200',
    'text-zinc-300': 'text-surface-300',
    'text-zinc-400': 'text-surface-400',
    'text-zinc-500': 'text-surface-500',
    'text-zinc-600': 'text-surface-600',
    'bg-zinc-800': 'bg-surface-800',
    'bg-zinc-700': 'bg-surface-700',
    'bg-zinc-600': 'bg-surface-600',
    'bg-zinc-500': 'bg-surface-500',
}

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print('Done.')
