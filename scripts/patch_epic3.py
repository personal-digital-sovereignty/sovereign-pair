import re
import sys

with open("core/src/api_trainer.rs", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update the executor loop end
target_block = """                                                    };
                                                    (symbol, format!("### Sovereign Open-Data Output:\\n{}", res), "Open-Data Ledger".to_string())
                                                }));
                                            }
                                        }
                                    }"""

new_block = """                                                    };
                                                    (symbol, format!("### Sovereign Open-Data Output:\\n{}", res), "Open-Data Ledger".to_string())
                                                }));
                                            }
                                        } else if let Some(fname) = func_n {
                                            // UNIVERSAL REFLEXIVE DISPATCHER
                                            let venv_python = dirs::data_local_dir().unwrap_or_default().join("sovereign-pair").join("sandbox").join("venv").join("bin").join("python3");
                                            let cur_dir = std::env::current_dir().unwrap_or_default();
                                            let script_path = if cur_dir.ends_with("core") { cur_dir.join("python_workers").join(format!("{}.py", fname)) } else { cur_dir.join("core").join("python_workers").join(format!("{}.py", fname)) };

                                            if script_path.exists() {
                                                let args_str = match func.get("arguments") {
                                                    Some(v) if v.is_object() => v.to_string(),
                                                    Some(v) if v.is_string() => v.as_str().unwrap().to_string(),
                                                    _ => "{}".to_string()
                                                };
                                                
                                                let _ = TRAINER_LOGS.send(format!("[Agentic Tool] Dispatch Reflexivo Invocando '{}'...", fname));
                                                let fname_clone = fname.to_string();
                                                
                                                join_handles.push(tokio::spawn(async move {
                                                    let output = tokio::process::Command::new(venv_python)
                                                        .arg(&script_path)
                                                        .arg(&args_str)
                                                        .output()
                                                        .await;
                                                        
                                                    let res = match output {
                                                        Ok(out) => {
                                                            let stdout = String::from_utf8_lossy(&out.stdout).to_string();
                                                            let stderr = String::from_utf8_lossy(&out.stderr).to_string();
                                                            if out.status.success() { stdout } else { format!("Error: {}", stderr) }
                                                        },
                                                        Err(e) => format!("Execution fail: {}", e)
                                                    };
                                                    (fname_clone.clone(), format!("### Return of {}:\\n{}", fname_clone, res), "Reflexive Sandbox".to_string())
                                                }));
                                            } else {
                                                let _ = TRAINER_LOGS.send(format!("⚠️ [Agentic Tool] Agent File '{}.py' não foi encontrado na pasta python_workers!", fname));
                                            }
                                        }
                                    }"""

if target_block in code:
    code = code.replace(target_block, new_block, 1)
    print("[+] Universal Dispatcher patched successfully")
else:
    print("[-] Could not find target_block in api_trainer.rs")

# 2. Update Thought Nanny (Dynamic strings)
nanny_target = """                            // Firewall Cognitivo: Fallback Universal (Thought Nanny)
                            if cycle == 1 || content.contains("\\"dispatch_sub_researcher\\"") || content.contains("\\"search_queries\\"") || content.contains("\\"fetch_financial_ticker\\"") || content.contains("\\"fetch_macroeconomy\\"") || content.contains("\\"type\\":\\"function\\"") || content.contains("\\"symbol\\"") || content.contains("\\"indicator\\") {"""

nanny_replacement_str = """                            // Firewall Cognitivo Reflexivo: Fallback (Thought Nanny)
                            let registry_names: Vec<String> = tools_schema.as_array().unwrap_or(&vec![]).iter().filter_map(|t| t.get("function").and_then(|f| f.get("name").and_then(|n| n.as_str().map(|s| s.to_string())))).collect();
                            let mut has_dynamic_tool = false;
                            for name in &registry_names {
                                if content.contains(name) || content.contains(&format!("\\\"{}\\\"", name)) {
                                    has_dynamic_tool = true;
                                    break;
                                }
                            }

                            if cycle == 1 || has_dynamic_tool || content.contains("\\"type\\":\\"function\\"") || content.contains("\\"search_queries\\"") || content.contains("\\"symbol\\"") || content.contains("\\"indicator\\") {"""

if nanny_target in code:
    code = code.replace(nanny_target, nanny_replacement_str, 1)
    print("[+] Thought Nanny if-condition patched successfully")
else:
    print("[-] Could not find Nanny target logic in api_trainer.rs")


system_override_target = """                                    "content": "[SYSTEM OVERRIDE]: Falha de Invocação de Ferramenta! Você gerou texto puro em vez de invocar a ferramenta no backend. O sistema AINDA não tem os dados necessários.\\n\\nSua ÚNICA saída aceita agora é FECHAR A BOCA e responder ESTRITAMENTE com o JSON correspondente à Variavel/Função (dispatch_sub_researcher, fetch_financial_ticker, fetch_macroeconomy ou execute_python_code). Não escreva NENHUM outro texto! APENAS O JSON NATIIVO.\\""""

system_override_new = """                                    "content": format!("[SYSTEM OVERRIDE]: Falha de Invocação de Ferramenta! Você gerou texto puro em vez de invocar a ferramenta no backend. O sistema AINDA não tem os dados necessários.\\n\\nSua ÚNICA saída aceita agora é FECHAR A BOCA e responder ESTRITAMENTE com o JSON correspondente à Variavel/Função ({}). Não escreva NENHUM outro texto! APENAS O JSON NATIVO.", registry_names.join(", "))"""

if system_override_target in code:
    code = code.replace(system_override_target, system_override_new)
    print("[+] Thought Nanny SYSTEM OVERRIDE patched successfully")
else:
    print("[-] Could not find Nanny SYSTEM OVERRIDE logic in api_trainer.rs")


with open("core/src/api_trainer.rs", "w", encoding="utf-8") as f:
    f.write(code)

