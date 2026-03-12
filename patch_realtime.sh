sed -i '/let stream = res.bytes_stream().map(move |result| {/,/Sse::new(stream).keep_alive(axum::response::sse::KeepAlive::new()).into_response()/c\
    let initial_events = futures_util::stream::iter(vec![\
        Ok::<Event, Infallible>(Event::default().data(\
            serde_json::to_string(&json!({"type": "response.created", "response": {}})).unwrap(),\
        )),\
        Ok::<Event, Infallible>(Event::default().data(\
            serde_json::to_string(&json!({"type": "response.output_item.added", "output_index": 0, "item": {"id": "msg_cibrido", "type": "message", "role": "assistant"}})).unwrap(),\
        )),\
    ]);\
\
    let tail_stream = res.bytes_stream().map(move |result| {\
        match result {\
            Ok(bytes) => {\
                if let Ok(chunk_str) = String::from_utf8(bytes.to_vec()) {\
                    for line in chunk_str.lines() {\
                        let line = line.trim();\
                        if line.is_empty() { continue; }\
\
                        if let Ok(ollama_resp) = serde_json::from_str::<Value>(line) {\
                            if let Some(msg_obj) = ollama_resp.get("message") {\
                                if let Some(content) = msg_obj.get("content").and_then(|c| c.as_str()) {\
                                    let json_str = serde_json::to_string(&json!({\
                                        "type": "response.output_text.delta",\
                                        "item_id": "msg_cibrido",\
                                        "output_index": 0,\
                                        "delta": content\
                                    })).unwrap_or_default();\
                                    return Ok::<Event, Infallible>(Event::default().data(json_str));\
                                }\
                            }\
                            \
                            if let Some(done) = ollama_resp.get("done").and_then(|d| d.as_bool()) {\
                                if done {\
                                    let json_str = serde_json::to_string(&json!({\
                                        "type": "response.output_item.done",\
                                        "output_index": 0,\
                                        "item": {\"id\": \"msg_cibrido\", \"type\": \"message\", \"role\": \"assistant\"}\
                                    })).unwrap_or_default();\
                                    return Ok::<Event, Infallible>(Event::default().data(json_str));\
                                }\
                            }\
                        }\
                    }\
                }\
                Ok::<Event, Infallible>(Event::default())\
            }\
            Err(_) => Ok::<Event, Infallible>(Event::default())\
        }\
    });\
    \
    let final_stream = initial_events.chain(tail_stream);\
\
    Sse::new(final_stream).keep_alive(axum::response::sse::KeepAlive::new()).into_response()\
' core/src/api.rs
