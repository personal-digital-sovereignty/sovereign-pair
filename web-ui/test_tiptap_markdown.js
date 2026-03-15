import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import { Table } from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableHeader from '@tiptap/extension-table-header';
import TableCell from '@tiptap/extension-table-cell';
import { Markdown } from 'tiptap-markdown';

// We mimic what the Vue component does
const SensusTableCell = TableCell.extend({
  name: 'tableCell',
  addAttributes() {
    return {
      sensusValue: { default: null },
      sensusError: { default: false }
    }
  }
});

const SensusTableHeader = TableHeader.extend({
  name: 'tableHeader',
  addAttributes() {
    return {
      sensusValue: { default: null },
      sensusError: { default: false }
    }
  }
});

// Create the Editor instance
const editor = new Editor({
  extensions: [
    StarterKit,
    Table, TableRow, SensusTableHeader, SensusTableCell,
    Markdown.configure({ html: false, transformPastedText: true, transformCopiedText: true })
  ],
  content: `
    <table>
      <tr><th>A</th><th>B</th></tr>
      <tr><td>1</td><td>=A1+1</td></tr>
    </table>
  `
});

setTimeout(() => {
  console.log("MARKDOWN OUTPUT:");
  console.log(editor.storage.markdown.getMarkdown());
}, 500);
