use std::path::Path;
use std::fs::File;
use std::io::Read;

pub fn parse_file(path: &str) -> Result<String, String> {
    let p = Path::new(path);
    let ext = p.extension().unwrap_or_default().to_string_lossy().to_lowercase();

    match ext.as_str() {
        "docx" => parse_docx(path),
        "pptx" | "odt" | "odp" => parse_ooxml_generic(path, ext.as_str()),
        "xlsx" | "ods" => parse_spreadsheet(path),
        "csv" => parse_csv(path),
        _ => {
            // Default text fallback
            std::fs::read_to_string(path).map_err(|e| e.to_string())
        }
    }
}

fn parse_docx(path: &str) -> Result<String, String> {
    // DOCX is a zip file, text is in word/document.xml
    let file = File::open(path).map_err(|e| format!("Failed to open file: {}", e))?;
    let mut archive = zip::ZipArchive::new(file).map_err(|e| format!("Failed to read zip: {}", e))?;
    
    let mut xml_file = match archive.by_name("word/document.xml") {
        Ok(f) => f,
        Err(_) => return Err("Invalid DOCX format: missing word/document.xml".to_string()),
    };
    
    let mut xml_content = String::new();
    xml_file.read_to_string(&mut xml_content).map_err(|e| format!("Failed to read XML: {}", e))?;
    
    extract_text_from_xml(&xml_content, b"w:t")
}

fn parse_ooxml_generic(path: &str, ext: &str) -> Result<String, String> {
    let file = File::open(path).map_err(|e| format!("Failed to open file: {}", e))?;
    let mut archive = zip::ZipArchive::new(file).map_err(|e| format!("Failed to read zip: {}", e))?;
    
    let target_file = match ext {
        "pptx" => "ppt/slides/slide", // Requires iterating through slide*.xml, handled below
        "odt" | "odp" => "content.xml",
        _ => return Err("Unsupported OOXML variant".to_string()),
    };

    if ext == "pptx" {
        let mut full_text = String::new();
        // PPTX splits content across multiple slide files
        for i in 1..999 {
            let slide_name = format!("ppt/slides/slide{}.xml", i);
            if let Ok(mut xml_file) = archive.by_name(&slide_name) {
                let mut xml_content = String::new();
                if xml_file.read_to_string(&mut xml_content).is_ok() {
                    if let Ok(slide_text) = extract_text_from_xml(&xml_content, b"a:t") {
                        full_text.push_str(&slide_text);
                        full_text.push_str("\n\n---\n\n"); // Slide separator
                    }
                }
            } else {
                break; // No more slides
            }
        }
        return Ok(full_text);
    }

    // For ODT/ODP
    let mut xml_file = match archive.by_name(target_file) {
        Ok(f) => f,
        Err(_) => return Err(format!("Invalid file format: missing {}", target_file)),
    };
    
    let mut xml_content = String::new();
    xml_file.read_to_string(&mut xml_content).map_err(|e| format!("Failed to read XML: {}", e))?;
    
    extract_text_from_xml(&xml_content, b"text:p") // ODF uses text:p for paragraphs
}

fn extract_text_from_xml(xml: &str, target_tag: &[u8]) -> Result<String, String> {
    use quick_xml::Reader;
    use quick_xml::events::Event;

    let mut reader = Reader::from_str(xml);
    let mut txt = String::new();
    let mut in_target = false;
    let mut buf = Vec::new();

    // Table state trackers for DOCX
    let mut in_table = false;
    let mut is_first_row = false;
    let mut columns = 0;

    // Formatting state trackers (DOCX)
    let mut is_bold = false;
    let mut is_italic = false;
    let mut is_underline = false;
    let mut heading_level = 0;
    let mut is_list = false;
    let mut new_paragraph = true;

    loop {
        match reader.read_event_into(&mut buf) {
            Ok(Event::Start(ref e)) => {
                let name = e.name();
                if name.as_ref() == target_tag {
                    in_target = true;
                } else if target_tag == b"w:t" {
                    match name.as_ref() {
                        b"w:p" => {
                            heading_level = 0;
                            is_list = false;
                            new_paragraph = true;
                            if !in_table {
                                txt.push_str("\n");
                            } else {
                                txt.push_str(" ");
                            }
                        },
                        b"w:r" => {
                            is_bold = false;
                            is_italic = false;
                            is_underline = false;
                        },
                        b"w:numPr" => {
                            is_list = true;
                        },
                        b"w:tbl" => {
                            in_table = true;
                            is_first_row = true;
                            txt.push_str("\n\n");
                        },
                        b"w:tr" => {
                            columns = 0;
                            txt.push_str("| ");
                        },
                        b"w:tc" => {
                            columns += 1;
                        },
                        _ => {}
                    }
                }
            }
            Ok(Event::Empty(ref e)) => {
                let name = e.name();
                if target_tag == b"w:t" {
                    match name.as_ref() {
                        b"w:b" => is_bold = true,
                        b"w:i" => is_italic = true,
                        b"w:u" => is_underline = true,
                        b"w:pStyle" => {
                            for attr in e.attributes().filter_map(|a| a.ok()) {
                                if attr.key.as_ref() == b"w:val" {
                                    let val = String::from_utf8_lossy(&attr.value).to_lowercase();
                                    if val.starts_with("heading") || val.starts_with("ttulo") {
                                        let lvl_str = val.replace("heading", "").replace("ttulo", "");
                                        if let Ok(lvl) = lvl_str.parse::<usize>() {
                                            heading_level = lvl;
                                        }
                                    }
                                }
                            }
                        },
                        _ => {}
                    }
                }
            }
            Ok(Event::End(ref e)) => {
                let name = e.name();
                if name.as_ref() == target_tag {
                    in_target = false;
                } else if target_tag == b"w:t" {
                    match name.as_ref() {
                        b"w:p" => {
                            if !in_table {
                                txt.push_str("\n");
                            }
                            new_paragraph = false;
                        },
                        b"w:tbl" => {
                            in_table = false;
                            txt.push_str("\n\n");
                        },
                        b"w:tr" => {
                            txt.push_str("\n");
                            if is_first_row && in_table {
                                txt.push_str("|");
                                for _ in 0..columns {
                                    txt.push_str("---|");
                                }
                                txt.push_str("\n");
                                is_first_row = false;
                            }
                        },
                        b"w:tc" => {
                            txt.push_str(" | ");
                        },
                        _ => {}
                    }
                }
            }
            Ok(Event::Text(e)) => {
                if in_target {
                    if let Ok(t) = e.unescape() {
                        let text = t.into_owned();
                        if !text.is_empty() {
                            if new_paragraph {
                                if heading_level > 0 && heading_level <= 6 {
                                    txt.push_str(&"#".repeat(heading_level));
                                    txt.push_str(" ");
                                } else if is_list {
                                    txt.push_str("- ");
                                }
                                new_paragraph = false;
                            }

                            if is_bold { txt.push_str("**"); }
                            if is_italic { txt.push_str("*"); }
                            if is_underline { txt.push_str("<u>"); }
                            
                            txt.push_str(&text);
                            
                            if is_underline { txt.push_str("</u>"); }
                            if is_italic { txt.push_str("*"); }
                            if is_bold { txt.push_str("**"); }
                        }
                    }
                }
            }
            Ok(Event::Eof) => break,
            Err(_) => break,
            _ => (),
        }
        buf.clear();
    }

    Ok(txt.trim().to_string())
}

fn parse_spreadsheet(path: &str) -> Result<String, String> {
    use calamine::{open_workbook_auto, Reader, Data};

    let mut workbook = open_workbook_auto(path).map_err(|e| format!("Failed to open workbook: {}", e))?;
    let mut result_md = String::new();

    let sheet_names = workbook.sheet_names().to_owned();

    for sheet in sheet_names {
        result_md.push_str(&format!("## Sheet: {}\n\n", sheet));
        if let Ok(range) = workbook.worksheet_range(&sheet) {
            let mut rows = range.rows();
            
            // Extract Headers
            if let Some(headers) = rows.next() {
                let header_row = headers.iter().map(|c| format!("{}", c)).collect::<Vec<String>>().join(" | ");
                result_md.push_str(&format!("| {} |\n", header_row));
                let sep_row = headers.iter().map(|_| "---".to_string()).collect::<Vec<String>>().join(" | ");
                result_md.push_str(&format!("| {} |\n", sep_row));
            }

            for row in rows {
                let md_row = row.iter().map(|c| match c {
                    Data::Empty => String::new(),
                    Data::String(s) => s.replace('\n', " ").replace('|', "\\|"),
                    Data::Float(f) => f.to_string(),
                    Data::Int(i) => i.to_string(),
                    Data::DateTime(_) | Data::DateTimeIso(_) | Data::DurationIso(_) => format!("{}", c),
                    Data::Bool(b) => b.to_string(),
                    Data::Error(e) => format!("ERR_{:?}", e),
                }).collect::<Vec<String>>().join(" | ");
                result_md.push_str(&format!("| {} |\n", md_row));
            }
            result_md.push_str("\n");
        }
    }

    Ok(result_md)
}

fn parse_csv(path: &str) -> Result<String, String> {
    let mut rdr = csv::ReaderBuilder::new()
        .flexible(true)
        .from_path(path)
        .map_err(|e| format!("Failed to open CSV: {}", e))?;

    let mut result_md = String::new();

    if let Ok(headers) = rdr.headers() {
        let header_row = headers.iter().map(|s: &str| s.replace('|', "\\|")).collect::<Vec<String>>().join(" | ");
        result_md.push_str(&format!("| {} |\n", header_row));
        let sep_row = headers.iter().map(|_| "---".to_string()).collect::<Vec<String>>().join(" | ");
        result_md.push_str(&format!("| {} |\n", sep_row));
    }

    for result in rdr.records() {
        if let Ok(record) = result {
            let md_row = record.iter().map(|s: &str| s.replace('\n', " ").replace('|', "\\|")).collect::<Vec<String>>().join(" | ");
            result_md.push_str(&format!("| {} |\n", md_row));
        }
    }

    Ok(result_md)
}
