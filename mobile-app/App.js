import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, ScrollView } from "react-native";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const send = async () => {
    if (!input) return;

    let newMessages = [...messages, { text: input, type: "user" }];
    setMessages(newMessages);

    let res = await fetch("http://YOUR_IP:5000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question: input })
    });

    let data = await res.json();

    setMessages([
      ...newMessages,
      {
        text: data.answer + "\n📌 " + data.article,
        type: "bot",
        source: data.source
      }
    ]);

    setInput("");
  };

  return (
    <View style={{ flex: 1, backgroundColor: "#343541", padding: 10 }}>
      
      <ScrollView style={{ flex: 1 }}>
        {messages.map((msg, i) => (
          <View key={i} style={{
            backgroundColor: msg.type === "user" ? "#444654" : "#2f2f38",
            padding: 10,
            margin: 5,
            borderRadius: 10
          }}>
            <Text style={{ color: "white" }}>{msg.text}</Text>
          </View>
        ))}
      </ScrollView>

      <View style={{ flexDirection: "row" }}>
        <TextInput
          value={input}
          onChangeText={setInput}
          placeholder="اسأل..."
          style={{
            flex: 1,
            backgroundColor: "white",
            padding: 10,
            borderRadius: 10
          }}
        />

        <TouchableOpacity onPress={send} style={{
          backgroundColor: "#10a37f",
          padding: 10,
          marginLeft: 5,
          borderRadius: 10
        }}>
          <Text style={{ color: "white" }}>Send</Text>
        </TouchableOpacity>
      </View>

    </View>
  );
}
