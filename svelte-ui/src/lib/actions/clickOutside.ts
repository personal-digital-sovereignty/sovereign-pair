export function clickOutside(node: HTMLElement, callback: () => void) {
    const handleClick = (e: MouseEvent) => {
        if (!node.contains(e.target as Node)) {
            callback();
        }
    };

    document.addEventListener('click', handleClick, true);

    return {
        destroy() {
            document.removeEventListener('click', handleClick, true);
        }
    };
}
