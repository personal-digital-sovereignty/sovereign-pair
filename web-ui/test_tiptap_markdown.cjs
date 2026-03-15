const { Editor } = require('@tiptap/core');
const StarterKit = require('@tiptap/starter-kit');
const Table = require('@tiptap/extension-table');
const TableRow = require('@tiptap/extension-table-row');
const TableHeader = require('@tiptap/extension-table-header');
const TableCell = require('@tiptap/extension-table-cell');
const { Markdown } = require('tiptap-markdown');

async function main() {
  const editor = new Editor({
    extensions: [
      StarterKit,
      Table, TableRow, TableHeader, TableCell,
      Markdown.configure({ html: false, transformPastedText: true, transformCopiedText: true })
    ],
    content: `
      <table>
        <tr><th>A</th><th>B</th></tr>
        <tr><td>1</td><td>=A1+1</td></tr>
      </table>
    `
  });

  console.log("MARKDOWN OUTPUT:");
  console.log(editor.storage.markdown.getMarkdown());
}

main();
