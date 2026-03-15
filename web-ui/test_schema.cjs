const { Editor } = require('@tiptap/core');
const Document = require('@tiptap/extension-document');
const Paragraph = require('@tiptap/extension-paragraph');
const Text = require('@tiptap/extension-text');
const Table = require('@tiptap/extension-table');
const TableRow = require('@tiptap/extension-table-row');
const TableHeader = require('@tiptap/extension-table-header');
const TableCell = require('@tiptap/extension-table-cell');

const StrictTableCell = TableCell.extend({
  name: 'tableCell',
  content: 'paragraph',
});

const editor = new Editor({
  extensions: [Document, Paragraph, Text, Table, TableRow, TableHeader, StrictTableCell],
  content: `
    <table>
      <tr><th><p>Header</p></th></tr>
      <tr><td><p>Hello</p><p></p></td></tr>
    </table>
  `
});

console.log(editor.getHTML());
