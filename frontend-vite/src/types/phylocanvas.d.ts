declare module '@phylocanvas/phylocanvas.gl' {
  interface TreeOptions {
    type?: 'radial' | 'rectangular';
    source?: string;
    alignLabels?: boolean;
    showLabels?: boolean;
    showLeafLabels?: boolean;
    showInternalLabels?: boolean;
    interactive?: boolean;
    zoom?: boolean;
    pan?: boolean;
    showScale?: boolean;
    nodeSize?: number;
    fontSize?: number;
    fontFamily?: string;
    strokeWidth?: number;
    strokeColour?: string;
    fillColour?: string;
    selectedFillColour?: string;
    highlightColour?: string;
    padding?: number;
  }

  interface TreeNode {
    id: string;
    label: string;
    originalLabel?: string;
    selected?: boolean;
    radius?: number;
    children?: TreeNode[];
    isLeaf?: boolean;
  }

  interface Tree {
    destroy(): void;
    render(): void;
    getLeafNodes(): TreeNode[];
    on(event: string, callback: (event: any) => void): void;
  }

  function createTree(element: HTMLElement, options: TreeOptions): Tree;

  export { createTree, Tree, TreeNode, TreeOptions };
} 