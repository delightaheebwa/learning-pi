<!-- source: https://platform.openai.com/docs/guides/structured-outputs | type: html | hash: da80a20fc7b2ca3c0cd2f7ac3830d5ec5ec9ce17132d426ae2909453f9153c50 | fetched: 2026-11-09 | truncated: true (code-sample blocks dropped) -->

JSON is one of the most widely used formats in the world for applications to exchange data.

 Structured Outputs is a feature that ensures the model will always generate responses that adhere to your supplied JSON Schema , so you don’t need to worry about the model omitting a required key, or hallucinating an invalid enum value.

 Some benefits of Structured Outputs include:

 Reliable type-safety: No need to validate or retry incorrectly formatted responses

 Explicit refusals: Safety-based model refusals are now programmatically detectable

 Simpler prompting: No need for strongly worded prompts to achieve consistent formatting

 In addition to supporting JSON Schema in the REST API, the OpenAI libraries for Python and JavaScript also let you define object schemas using pydantic.BaseModel and z.object respectively. Below, you can see how to extract information from unstructured text that conforms to a schema defined in code.

 The Ruby SDK supports schemas defined with Sorbet T::Struct and returns typed parsed results.

 Getting a structured response
 Python 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 import OpenAI from "openai"; 
 import { zodResponseFormat } from "openai/helpers/zod"; 
 import { z } from "zod"; 
 
 const openai = new OpenAI(); 
 
 const CalendarEvent = z.object({ 
 name: z.string(), 
 date: z.string(), 
 participants: z.array(z.string()), 
 }); 
 
 const completion = await openai.chat.completions.parse({ 
 model: "gpt-6-astra", 
 messages: [ 
 { role: "system", content: "Extract the event information." }, 
 { 
 role: "user", 
 content: "Alice and Bob are going to a science fair on Friday.", 
 }, 
 ], 
 response_format: zodResponseFormat(CalendarEvent, "event"), 
 }); 
 
 const event = completion.choices[0].message.parsed; 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 from pydantic import BaseModel 
 from openai import OpenAI 
 
 client = OpenAI() 

 class CalendarEvent ( BaseModel ): 
 name: str 
 date: str 
 participants: list[ str ] 

 completion = client.chat.completions.parse( 
 model = "gpt-6-astra" , 
 messages = [ 
 { "role" : "system" , "content" : "Extract the event information." }, 
 { 
 "role" : "user" , 
 "content" : "Alice and Bob are going to a science fair on Friday." , 
 }, 
 ], 
 response_format = CalendarEvent, 
 ) 
 
 event = completion.choices[ 0 ].message.parsed 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 package main 
 
 import ( 
 "context" 
 "fmt" 
 
 "github.com/openai/openai-go/v3" 
 "github.com/openai/openai-go/v3/shared" 
 ) 
 
 func main() { 
 client := openai.NewClient() 
 schema := map[string]any{ 
 "type": "object", 
 "properties": map[string]any{ 
 "name": map[string]any{"type": "string"}, 
 "date": map[string]any{"type": "string"}, 
 "participants": map[string]any{"type": "array", "items": map[string]any{"type": "string"}}, 
 }, 
 "required": []string{"name", "date", "participants"}, 
 "additionalProperties": false, 
 } 
 
 completion, err := client.Chat.Completions.New(context.Background(), openai.ChatCompletionNewParams{ 
 Model: "gpt-6-astra", 
 Messages: []openai.ChatCompletionMessageParamUnion{ 
 openai.SystemMessage("Extract the event information."), 
 openai.UserMessage("Alice and Bob are going to a science fair on Friday."), 
 }, 
 ResponseFormat: openai.ChatCompletionNewParamsResponseFormatUnion{ 
 OfJSONSchema: &shared.ResponseFormatJSONSchemaParam{JSONSchema: shared.ResponseFormatJSONSchemaJSONSchemaParam{ 
 Name: "event", Schema: schema, Strict: openai.Bool(true), 
 }}, 
 }, 
 }) 
 if err != nil { 
 panic(err) 
 } 
 
 fmt.Println(completion.Choices[0].Message.Content) 
 } 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 import com.openai.client.OpenAIClient; 
 import com.openai.client.okhttp.OpenAIOkHttpClient; 
 import com.openai.core.JsonValue; 
 import com.openai.models.chat.completions.ChatCompletionCreateParams; 
 import java.util.List; 
 import java.util.Map; 
 
 Map<String, Object> schema = 
 Map.of( 
 "type", 
 "object", 
 "properties", 
 Map.of( 
 "name", Map.of("type", "string"), 
 "date", Map.of("type", "string"), 
 "participants", Map.of("type", "array", "items", Map.of("type", "string"))), 
 "required", 
 List.of("name", "date", "participants"), 
 "additionalProperties", 
 false); 
 
 ChatCompletionCreateParams params = 
 ChatCompletionCreateParams.builder() 
 .model("gpt-6-astra") 
 .addSystemMessage("Extract the event information.") 
 .addUserMessage("Alice and Bob are going to a science fair on Friday.") 
 .putAdditionalBodyProperty( 
 "response_format", 
 JsonValue.from( 
 Map.of( 
 "type", 
 "json_schema", 
 "json_schema", 
 Map.of("name", "event", "strict", true, "schema", schema)))) 
 .build(); 
 
 client.chat().completions().create(params).choices().stream() 
 .flatMap(choice -> choice.message().content().stream()) 
 .forEach(System.out::println); 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 using OpenAI.Chat; 
 
 string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!; 
 string model = "gpt-6-astra"; 
 ChatClient client = new(model, key); 
 
 BinaryData schema = BinaryData.FromString( 
 """ 
 { 
 "type": "object", 
 "properties": { 
 "name": { "type": "string" }, 
 "date": { "type": "string" }, 
 "participants": { 
 "type": "array", 
 "items": { "type": "string" } 
 } 
 }, 
 "required": ["name", "date", "participants"], 
 "additionalProperties": false 
 } 
 """ 
 ); 
 ChatCompletionOptions options = new() 
 { 
 ResponseFormat = ChatResponseFormat.CreateJsonSchemaFormat( 
 "event", 
 schema, 
 jsonSchemaIsStrict: true 
 ), 
 }; 
 ChatCompletion completion = await client.CompleteChatAsync( 
 [ 
 new SystemChatMessage("Extract the event information."), 
 new UserChatMessage( 
 "Alice and Bob are going to a science fair on Friday." 
 ), 
 ], 
 options 
 ); 
 
 Console.WriteLine(completion.Content[0].Text); 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 # gem install openai sorbet-runtime 
 require "openai" 
 require "openai/helpers/sorbet" 
 
 class CalendarEvent < T::Struct 
 const :name, String 
 const :date, String 
 const :participants, T::Array[String] 
 end 
 
 client = OpenAI::Client.new 
 schema = OpenAI::StructuredOutput.from_sorbet(CalendarEvent) 
 
 completion = client.chat.completions.create( 
 model: "gpt-6-astra", 
 messages: [ 
 { 
 role: :system, 
 content: "Extract the event information." 
 }, 
 { 
 role: :user, 
 content: "Alice and Bob are going to a science fair on Friday." 
 } 
 ], 
 response_format: schema 
 ) 
 
 choice = completion.choices.fetch(0) 
 raise "Completion ended with reason: #{choice.finish_reason}" unless choice.finish_reason.to_s == "stop" 
 raise "The model refused the request" if choice.message.refusal 
 
 event = T.cast(choice.message.parsed, CalendarEvent) 
 puts(event.name, event.date, event.participants.join(", ")) 

 Getting a structured response
 Python 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 import OpenAI from "openai"; 
 import { zodTextFormat } from "openai/helpers/zod"; 
 import { z } from "zod"; 
 
 const openai = new OpenAI(); 
 
 const CalendarEvent = z.object({ 
 name: z.string(), 
 date: z.string(), 
 participants: z.array(z.string()), 
 }); 
 
 const response = await openai.responses.parse({ 
 model: "gpt-6-astra", 
 input: [ 
 { role: "system", content: "Extract the event information." }, 
 { 
 role: "user", 
 content: "Alice and Bob are going to a science fair on Friday.", 
 }, 
 ], 
 text: { 
 format: zodTextFormat(CalendarEvent, "event"), 
 }, 
 }); 
 
 const event = response.output_parsed; 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 from openai import OpenAI 
 from pydantic import BaseModel 
 
 client = OpenAI() 

 class CalendarEvent ( BaseModel ): 
 name: str 
 date: str 
 participants: list[ str ] 

 response = client.responses.parse( 
 model = "gpt-6-astra" , 
 input = [ 
 { "role" : "system" , "content" : "Extract the event information." }, 
 { 
 "role" : "user" , 
 "content" : "Alice and Bob are going to a science fair on Friday." , 
 }, 
 ], 
 text_format = CalendarEvent, 
 ) 
 
 event = response.output_parsed 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 package main 
 
 import ( 
 "context" 
 "fmt" 
 
 "github.com/openai/openai-go/v3" 
 "github.com/openai/openai-go/v3/responses" 
 ) 
 
 func main() { 
 client := openai.NewClient() 
 schema := map[string]any{ 
 "type": "object", 
 "properties": map[string]any{ 
 "name": map[string]any{"type": "string"}, 
 "date": map[string]any{"type": "string"}, 
 "participants": map[string]any{"type": "array", "items": map[string]any{"type": "string"}}, 
 }, 
 "required": []string{"name", "date", "participants"}, 
 "additionalProperties": false, 
 } 
 
 response, err := client.Responses.New(context.Background(), responses.ResponseNewParams{ 
 Model: "gpt-6-astra", 
 Input: responses.ResponseNewParamsInputUnion{OfInputItemList: responses.ResponseInputParam{ 
 responses.ResponseInputItemParamOfMessage( 
 responses.ResponseInputMessageContentListParam{responses.ResponseInputContentParamOfInputText("Extract the event information.")}, 
 responses.EasyInputMessageRoleSystem, 
 ), 
 responses.ResponseInputItemParamOfMessage( 
 responses.ResponseInputMessageContentListParam{responses.ResponseInputContentParamOfInputText("Alice and Bob are going to a science fair on Friday.")}, 
 responses.EasyInputMessageRoleUser, 
 ), 
 }}, 
 Text: responses.ResponseTextConfigParam{Format: responses.ResponseFormatTextConfigUnionParam{ 
 OfJSONSchema: &responses.ResponseFormatTextJSONSchemaConfigParam{Name: "event", Schema: schema, Strict: openai.Bool(true)}, 
 }}, 
 }) 
 if err != nil { 
 panic(err) 
 } 
 
 fmt.Println(response.OutputText()) 
 } 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 
 48 
 49 
 50 
 51 
 52 
 53 
 54 
 55 
 56 
 57 
 58 import com.openai.client.OpenAIClient; 
 import com.openai.client.okhttp.OpenAIOkHttpClient; 
 import com.openai.core.JsonValue; 
 import com.openai.models.responses.EasyInputMessage; 
 import com.openai.models.responses.ResponseCreateParams; 
 import com.openai.models.responses.ResponseFormatTextJsonSchemaConfig; 
 import com.openai.models.responses.ResponseInputItem; 
 import com.openai.models.responses.ResponseTextConfig; 
 import java.util.List; 
 import java.util.Map; 
 
 Map<String, Object> schema = 
 Map.of( 
 "type", 
 "object", 
 "properties", 
 Map.of( 
 "name", Map.of("type", "string"), 
 "date", Map.of("type", "string"), 
 "participants", Map.of("type", "array", "items", Map.of("type", "string"))), 
 "required", 
 List.of("name", "date", "participants"), 
 "additionalProperties", 
 false); 
 
 ResponseCreateParams params = 
 ResponseCreateParams.builder() 
 .model("gpt-6-astra") 
 .inputOfResponse( 
 List.of( 
 ResponseInputItem.ofEasyInputMessage( 
 EasyInputMessage.builder() 
 .role(EasyInputMessage.Role.SYSTEM) 
 .content("Extract the event information.") 
 .build()), 
 ResponseInputItem.ofEasyInputMessage( 
 EasyInputMessage.builder() 
 .role(EasyInputMessage.Role.USER) 
 .content("Alice and Bob are going to a science fair on Friday.") 
 .build()))) 
 .text( 
 ResponseTextConfig.builder() 
 .format( 
 ResponseFormatTextJsonSchemaConfig.builder() 
 .name("event") 
 .strict(true) 
 .schema( 
 JsonValue.from(schema) 
 .convert(ResponseFormatTextJsonSchemaConfig.Schema.class)) 
 .build()) 
 .build()) 
 .build(); 
 
 client.responses().create(params).output().stream() 
 .flatMap(item -> item.message().stream()) 
 .flatMap(message -> message.content().stream()) 
 .flatMap(content -> content.outputText().stream()) 
 .forEach(text -> System.out.println(text.text())); 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 using OpenAI.Responses; 
 #pragma warning disable OPENAI001 
 
 string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!; 
 ResponsesClient client = new(key); 
 
 BinaryData schema = BinaryData.FromString( 
 """ 
 { 
 "type": "object", 
 "properties": { 
 "name": { "type": "string" }, 
 "date": { "type": "string" }, 
 "participants": { 
 "type": "array", 
 "items": { "type": "string" } 
 } 
 }, 
 "required": ["name", "date", "participants"], 
 "additionalProperties": false 
 } 
 """ 
 ); 
 CreateResponseOptions options = new() 
 { 
 Model = "gpt-6-astra", 
 TextOptions = new ResponseTextOptions 
 { 
 TextFormat = ResponseTextFormat.CreateJsonSchemaFormat( 
 "event", 
 schema, 
 jsonSchemaIsStrict: true 
 ), 
 }, 
 }; 
 options.InputItems.Add( 
 ResponseItem.CreateSystemMessageItem("Extract the event information.") 
 ); 
 options.InputItems.Add( 
 ResponseItem.CreateUserMessageItem( 
 "Alice and Bob are going to a science fair on Friday." 
 ) 
 ); 
 
 ResponseResult response = await client.CreateResponseAsync(options); 

[... middle: ~15k lines of multi-language code samples omitted by Scout (truncated: true) ...]

Tips and best practices

 Handling user-generated input 

 If your application is using user-generated input, make sure your prompt includes instructions on how to handle situations where the input cannot result in a valid response.

 The model will always try to adhere to the provided schema, which can result in hallucinations if the input is completely unrelated to the schema.

 You could include language in your prompt to specify that you want to return empty parameters, or a specific sentence, if the model detects that the input is incompatible with the task.

 Handling mistakes 

 Structured Outputs can still contain mistakes. If you see mistakes, try adjusting your instructions, providing examples in the system instructions, or splitting tasks into simpler subtasks. Refer to the prompt engineering guide for more guidance on how to tweak your inputs.

 Avoid JSON schema divergence 

 To prevent your JSON Schema and corresponding types in your programming language from diverging, we strongly recommend using native SDK schema helpers where available.

 If you prefer to specify the JSON schema directly, you could add CI rules that flag when either the JSON schema or underlying data objects are edited, or add a CI step that automatically generates the JSON Schema from type definitions (or vice-versa).

 Streaming 

 You can use streaming to process model responses or function call arguments as they are being generated, and parse them as structured data.

 That way, you don’t have to wait for the entire response to complete before handling it.
This is particularly useful if you would like to display JSON fields one by one, or handle function call arguments as soon as they are available.

 We recommend relying on the SDKs to handle streaming with Structured Outputs.

 You can find an example of how to stream function call arguments without the SDK stream helper in the function calling guide .
 Here is how you can stream a model response with the stream helper:
 
 Python 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 import OpenAI from "openai"; 
 import { zodResponseFormat } from "openai/helpers/zod"; 
 import { z } from "zod"; 
 
 const openai = new OpenAI(); 
 
 const EntitiesSchema = z.object({ 
 attributes: z.array(z.string()), 
 colors: z.array(z.string()), 
 animals: z.array(z.string()), 
 }); 
 
 const stream = openai.chat.completions 
 .stream({ 
 model: "gpt-6-astra", 
 messages: [ 
 { role: "system", content: "Extract entities from the input text" }, 
 { 
 role: "user", 
 content: 
 "The quick brown fox jumps over the lazy dog with piercing blue eyes", 
 }, 
 ], 
 response_format: zodResponseFormat(EntitiesSchema, "entities"), 
 }) 
 .on("refusal.done", () => console.log("request refused")) 
 .on("content.delta", ({ snapshot, parsed }) => { 
 console.log("content:", snapshot); 
 console.log("parsed:", parsed); 
 console.log(); 
 }) 
 .on("content.done", (props) => { 
 console.log(props); 
 }); 
 
 await stream.done(); 
 
 const finalCompletion = await stream.finalChatCompletion(); 
 
 console.log(finalCompletion); 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 from pydantic import BaseModel 
 from openai import OpenAI 

 class EntitiesModel ( BaseModel ): 
 attributes: list[ str ] 
 colors: list[ str ] 
 animals: list[ str ] 

 client = OpenAI() 
 
 with client.beta.chat.completions.stream( 
 model = "gpt-6-astra" , 
 messages = [ 
 { "role" : "system" , "content" : "Extract entities from the input text" }, 
 { 
 "role" : "user" , 
 "content" : "The quick brown fox jumps over the lazy dog with piercing blue eyes" , 
 }, 
 ], 
 response_format = EntitiesModel, 
 ) as stream: 
 for event in stream: 
 if event.type == "content.delta" : 
 if event.parsed is not None : # Print the parsed data as JSON 
 print ( "content.delta parsed:" , event.parsed) 
 elif event.type == "content.done" : 
 print ( "content.done" ) 
 elif event.type == "error" : 
 print ( "Error in stream:" , event.error) 
 
 final_completion = stream.get_final_completion() 
 print ( "Final completion:" , final_completion) 

 You can also use the stream helper to parse function call arguments:
 
 Python 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 import { zodFunction } from "openai/helpers/zod"; 
 import OpenAI from "openai/index"; 
 import { z } from "zod"; 
 
 const GetWeatherArgs = z.object({ 
 city: z.string(), 
 country: z.string(), 
 }); 
 
 const client = new OpenAI(); 
 
 const stream = client.chat.completions 
 .stream({ 
 model: "gpt-5.6-terra", 
 reasoning_effort: "none", 
 parallel_tool_calls: true, 
 messages: [ 
 { 
 role: "user", 
 content: "What's the weather like in SF and London?", 
 }, 
 ], 
 tools: [zodFunction({ name: "get_weather", parameters: GetWeatherArgs })], 
 }) 
 .on("tool_calls.function.arguments.delta", (props) => 
 console.log("tool_calls.function.arguments.delta", props) 
 ) 
 .on("tool_calls.function.arguments.done", (props) => 
 console.log("tool_calls.function.arguments.done", props) 
 ) 
 .on("refusal.delta", ({ delta }) => { 
 process.stdout.write(delta); 
 }) 
 .on("refusal.done", () => console.log("request refused")); 
 
 const completion = await stream.finalChatCompletion(); 
 
 console.log("final completion:", completion); 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 from pydantic import BaseModel 
 import openai 
 from openai import OpenAI 

 class GetWeather ( BaseModel ): 
 city: str 
 country: str 

 client = OpenAI() 
 
 with client.beta.chat.completions.stream( 
 model = "gpt-5.6-terra" , 
 reasoning_effort = "none" , 
 messages = [ 
 { 
 "role" : "user" , 
 "content" : "What's the weather like in SF and London?" , 
 }, 
 ], 
 tools = [ 
 openai.pydantic_function_tool(GetWeather, name = "get_weather" ), 
 ], 
 parallel_tool_calls = True , 
 ) as stream: 
 for event in stream: 
 if ( 
 event.type == "tool_calls.function.arguments.delta" 
 or event.type == "tool_calls.function.arguments.done" 
 ): 
 print (event) 
 
 print (stream.get_final_completion()) 

 Python 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 import { OpenAI } from "openai"; 
 import { zodTextFormat } from "openai/helpers/zod"; 
 import { z } from "zod"; 
 
 const EntitiesSchema = z.object({ 
 attributes: z.array(z.string()), 
 colors: z.array(z.string()), 
 animals: z.array(z.string()), 
 }); 
 
 const openai = new OpenAI(); 
 const stream = openai.responses 
 .stream({ 
 model: "gpt-6-astra", 
 input: [ 
 { role: "user", content: "What's the weather like in Paris today?" }, 
 ], 
 text: { 
 format: zodTextFormat(EntitiesSchema, "entities"), 
 }, 
 }) 
 .on("response.refusal.delta", (event) => { 
 process.stdout.write(event.delta); 
 }) 
 .on("response.output_text.delta", (event) => { 
 process.stdout.write(event.delta); 
 }) 
 .on("response.output_text.done", () => { 
 process.stdout.write("\n"); 
 }) 
 .on("error", (error) => { 
 console.error(error); 
 }); 
 
 const result = await stream.finalResponse(); 
 
 console.log(result); 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 from openai import OpenAI 
 from pydantic import BaseModel 

 class EntitiesModel ( BaseModel ): 
 attributes: list[ str ] 
 colors: list[ str ] 
 animals: list[ str ] 

 client = OpenAI() 
 
 with client.responses.stream( 
 model = "gpt-6-astra" , 
 input = [ 
 { "role" : "system" , "content" : "Extract entities from the input text" }, 
 { 
 "role" : "user" , 
 "content" : "The quick brown fox jumps over the lazy dog with piercing blue eyes" , 
 }, 
 ], 
 text_format = EntitiesModel, 
 ) as stream: 
 for event in stream: 
 if event.type == "response.refusal.delta" : 
 print (event.delta, end = "" ) 
 elif event.type == "response.output_text.delta" : 
 print (event.delta, end = "" ) 
 elif event.type == "response.error" : 
 print (event.error, end = "" ) 
 elif event.type == "response.completed" : 
 print ( "Completed" ) # print(event.response.output) 
 
 final_response = stream.get_final_response() 
 print (final_response) 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 
 48 
 49 
 50 
 51 
 52 
 53 
 54 
 55 
 56 
 57 
 58 
 59 
 60 
 61 
 62 
 63 
 64 
 65 
 66 
 67 
 68 
 69 
 70 
 71 
 72 
 73 
 74 
 75 
 76 
 77 
 78 
 79 
 80 
 81 
 82 
 83 
 84 
 85 
 86 import com.openai.client.OpenAIClient; 
 import com.openai.client.okhttp.OpenAIOkHttpClient; 
 import com.openai.core.JsonValue; 
 import com.openai.core.http.StreamResponse; 
 import com.openai.models.responses.EasyInputMessage; 
 import com.openai.models.responses.ResponseCreateParams; 
 import com.openai.models.responses.ResponseFormatTextJsonSchemaConfig; 
 import com.openai.models.responses.ResponseInputItem; 
 import com.openai.models.responses.ResponseStreamEvent; 
 import com.openai.models.responses.ResponseTextConfig; 
 import java.util.List; 
 import java.util.Map; 
 
 ResponseCreateParams params = 
 ResponseCreateParams.builder() 
 .model("gpt-6-astra") 
 .inputOfResponse( 
 List.of( 
 ResponseInputItem.ofEasyInputMessage( 
 EasyInputMessage.builder() 
 .role(EasyInputMessage.Role.SYSTEM) 
 .content("Extract entities from the input text") 
 .build()), 
 ResponseInputItem.ofEasyInputMessage( 
 EasyInputMessage.builder() 
 .role(EasyInputMessage.Role.USER) 
 .content( 
 "The quick brown fox jumps over the lazy dog with piercing blue eyes") 
 .build()))) 
 .text( 
 ResponseTextConfig.builder() 
 .format( 
 ResponseFormatTextJsonSchemaConfig.builder() 
 .name("entities") 
 .strict(true) 
 .schema( 
 ResponseFormatTextJsonSchemaConfig.Schema.builder() 
 .putAdditionalProperty("type", JsonValue.from("object")) 
 .putAdditionalProperty( 
 "properties", 
 JsonValue.from( 
 Map.of( 
 "attributes", 
 Map.of( 
 "type", 
 "array", 
 "items", 
 Map.of("type", "string")), 
 "colors", 
 Map.of( 
 "type", 
 "array", 
 "items", 
 Map.of("type", "string")), 
 "animals", 
 Map.of( 
 "type", 
 "array", 
 "items", 
 Map.of("type", "string"))))) 
 .putAdditionalProperty( 
 "required", 
 JsonValue.from(List.of("attributes", "colors", "animals"))) 
 .putAdditionalProperty( 
 "additionalProperties", JsonValue.from(false)) 
 .build()) 
 .build()) 
 .build()) 
 .build(); 
 
 try (StreamResponse<ResponseStreamEvent> stream = client.responses().createStreaming(params)) { 
 stream.stream() 
 .forEach( 
 event -> { 
 event.outputTextDelta().ifPresent(delta -> System.out.print(delta.delta())); 
 event.refusalDelta().ifPresent(refusal -> System.out.print(refusal.delta())); 
 event.error().ifPresent(error -> System.out.println(error.message())); 
 event 
 .completed() 
 .ifPresent( 
 completed -> { 
 System.out.println("Completed"); 
 System.out.println(completed.response()); 
 }); 
 }); 
 } 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 
 48 
 49 
 50 
 51 
 52 
 53 
 54 
 55 
 56 require "openai" 
 
 client = OpenAI::Client.new 
 entities_schema = { 
 type: :object, 
 properties: { 
 attributes: { 
 type: :array, 
 items: { type: :string } 
 }, 
 colors: { 
 type: :array, 
 items: { type: :string } 
 }, 
 animals: { 
 type: :array, 
 items: { type: :string } 
 } 
 }, 
 required: %w[attributes colors animals], 
 additionalProperties: false 
 } 
 
 stream = client.responses.stream( 
 model: "gpt-6-astra", 
 input: [ 
 { 
 role: :system, 
 content: "Extract entities from the input text." 
 }, 
 { 
 role: :user, 
 content: "The quick brown fox jumps over the lazy dog with piercing blue eyes." 
 } 
 ], 
 text: { 
 format: { 
 type: :json_schema, 
 name: "entities", 
 strict: true, 
 schema: entities_schema 
 } 
 } 
 ) 
 
 stream.each do |event| 
 case event 
 when OpenAI::Models::Responses::ResponseRefusalDeltaEvent, 
 OpenAI::Models::Responses::ResponseTextDeltaEvent 
 print(event.delta) 
 when OpenAI::Models::Responses::ResponseErrorEvent 
 warn(event.message) 
 when OpenAI::Models::Responses::ResponseCompletedEvent 
 puts("\nCompleted") 
 end 
 end 

 Supported schemas 

 Structured Outputs supports a subset of the JSON Schema language.

 Supported types

 The following types are supported for Structured Outputs:

 String

 Number

 Boolean

 Integer

 Object

 Array

 Enum

 anyOf

 Supported properties

 In addition to specifying the type of a property, you can specify a selection of additional constraints:

 Supported string properties: 

 pattern — A regular expression that the string must match.

 format — Predefined formats for strings. Currently supported:
 
 date-time 

 time 

 date 

 duration 

 email 

 hostname 

 ipv4 

 ipv6 

 uuid 

 Supported number properties: 

 multipleOf — The number must be a multiple of this value.

 maximum — The number must be less than or equal to this value.

 exclusiveMaximum — The number must be less than this value.

 minimum — The number must be greater than or equal to this value.

 exclusiveMinimum — The number must be greater than this value.

 Supported array properties: 

 minItems — The array must have at least this many items.

 maxItems — The array must have at most this many items.

 Here are some examples on how you can use these type restrictions:

 String Restrictions Number Restrictions 
 
 String Restrictions
 
 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 { 
 "name" : "user_data" , 
 "strict" : true , 
 "schema" : { 
 "type" : "object" , 
 "properties" : { 
 "name" : { 
 "type" : "string" , 
 "description" : "The name of the user" 
 }, 
 "username" : { 
 "type" : "string" , 
 "description" : "The username of the user. Must start with @" , 
 "pattern" : "^@[a-zA-Z0-9_]+$" 
 }, 
 "email" : { 
 "type" : "string" , 
 "description" : "The email of the user" , 
 "format" : "email" 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ 
 "name" , "username" , "email" 
 ] 
 } 
 } 

 Number Restrictions
 
 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 { 
 "name" : "weather_data" , 
 "strict" : true , 
 "schema" : { 
 "type" : "object" , 
 "properties" : { 
 "location" : { 
 "type" : "string" , 
 "description" : "The location to get the weather for" 
 }, 
 "unit" : { 
 "type" : [ "string" , "null" ], 
 "description" : "The unit to return the temperature in" , 
 "enum" : [ "F" , "C" ] 
 }, 
 "value" : { 
 "type" : "number" , 
 "description" : "The actual temperature value in the location" , 
 "minimum" : -130 , 
 "maximum" : 130 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ 
 "location" , "unit" , "value" 
 ] 
 } 
 } 

 Note these constraints are not yet supported for fine-tuned
models .

 Root objects must not be anyOf and must be an object

 Note that the root level object of a schema must be an object, and not use anyOf . A pattern that appears in Zod (as one example) is using a discriminated union, which produces an anyOf at the top level. So code such as the following won’t work:

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 import { z } from "zod" ; 
 import { zodResponseFormat } from "openai/helpers/zod" ; 
 
 const BaseResponseSchema = z. object ({ 
 /* ... */ 
 }); 
 const UnsuccessfulResponseSchema = z. object ({ 
 /* ... */ 
 }); 
 
 const finalSchema = z. discriminatedUnion ( "status" , [ 
 BaseResponseSchema, 
 UnsuccessfulResponseSchema, 
 ]); 
 
 // Invalid JSON Schema for Structured Outputs 
 const json = zodResponseFormat (finalSchema, "final_schema" ); 

 All fields must be required 

 To use Structured Outputs, all fields or function parameters must be specified as required .

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 { 
 "name" : "get_weather" , 
 "description" : "Fetches the weather in the given location" , 
 "strict" : true , 
 "parameters" : { 
 "type" : "object" , 
 "properties" : { 
 "location" : { 
 "type" : "string" , 
 "description" : "The location to get the weather for" 
 }, 
 "unit" : { 
 "type" : "string" , 
 "description" : "The unit to return the temperature in" , 
 "enum" : [ "F" , "C" ] 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ "location" , "unit" ] 
 } 
 } 

 Although all fields must be required (and the model will return a value for each parameter), it is possible to emulate an optional parameter by using a union type with null .

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 { 
 "name" : "get_weather" , 
 "description" : "Fetches the weather in the given location" , 
 "strict" : true , 
 "parameters" : { 
 "type" : "object" , 
 "properties" : { 
 "location" : { 
 "type" : "string" , 
 "description" : "The location to get the weather for" 
 }, 
 "unit" : { 
 "type" : [ "string" , "null" ], 
 "description" : "The unit to return the temperature in" , 
 "enum" : [ "F" , "C" ] 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ 
 "location" , "unit" 
 ] 
 } 
 } 

 Objects have limitations on nesting depth and size

 A schema may have up to 5000 object properties total, with up to 10 levels of nesting.

 Limitations on total string size

 In a schema, total string length of all property names, definition names, enum values, and const values cannot exceed 120,000 characters.

 Limitations on enum size

 A schema may have up to 1000 enum values across all enum properties.

 For a single enum property with string values, the total string length of all enum values cannot exceed 15,000 characters when there are more than 250 enum values.

 additionalProperties: false must always be set in objects

 additionalProperties controls whether it is allowable for an object to contain additional keys / values that were not defined in the JSON Schema.

 Structured Outputs only supports generating specified keys / values, so we require developers to set additionalProperties: false to opt into Structured Outputs.

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 { 
 "name" : "get_weather" , 
 "description" : "Fetches the weather in the given location" , 
 "strict" : true , 
 "schema" : { 
 "type" : "object" , 
 "properties" : { 
 "location" : { 
 "type" : "string" , 
 "description" : "The location to get the weather for" 
 }, 
 "unit" : { 
 "type" : "string" , 
 "description" : "The unit to return the temperature in" , 
 "enum" : [ "F" , "C" ] 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ 
 "location" , "unit" 
 ] 
 } 
 } 

 Key ordering

 When using Structured Outputs, outputs will be produced in the same order as the ordering of keys in the schema.

 Some type-specific keywords are not yet supported

 Composition: allOf , not , dependentRequired , dependentSchemas , if , then , else 

 For fine-tuned models, we additionally do not support the following:

 For strings: minLength , maxLength , pattern , format 

 For numbers: minimum , maximum , multipleOf 

 For objects: patternProperties 

 For arrays: minItems , maxItems 

 If you turn on Structured Outputs by supplying strict: true and call the API with an unsupported JSON Schema, you will receive an error.

 For anyOf , the nested schemas must each be a valid JSON Schema per this subset

 Here’s an example supported anyOf schema:

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 
 48 
 49 
 50 
 51 
 52 
 53 
 54 
 55 
 56 { 
 "type" : "object" , 
 "properties" : { 
 "item" : { 
 "anyOf" : [ 
 { 
 "type" : "object" , 
 "description" : "The user object to insert into the database" , 
 "properties" : { 
 "name" : { 
 "type" : "string" , 
 "description" : "The name of the user" 
 }, 
 "age" : { 
 "type" : "number" , 
 "description" : "The age of the user" 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ 
 "name" , 
 "age" 
 ] 
 }, 
 { 
 "type" : "object" , 
 "description" : "The address object to insert into the database" , 
 "properties" : { 
 "number" : { 
 "type" : "string" , 
 "description" : "The number of the address. Eg. for 123 main st, this would be 123" 
 }, 
 "street" : { 
 "type" : "string" , 
 "description" : "The street name. Eg. for 123 main st, this would be main st" 
 }, 
 "city" : { 
 "type" : "string" , 
 "description" : "The city of the address" 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ 
 "number" , 
 "street" , 
 "city" 
 ] 
 } 
 ] 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ 
 "item" 
 ] 
 } 

 Definitions are supported

 You can use definitions to define subschemas which are referenced throughout your schema. The following is a simple example.

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 { 
 "type" : "object" , 
 "properties" : { 
 "steps" : { 
 "type" : "array" , 
 "items" : { 
 "$ref" : "#/$defs/step" 
 } 
 }, 
 "final_answer" : { 
 "type" : "string" 
 } 
 }, 
 "$defs" : { 
 "step" : { 
 "type" : "object" , 
 "properties" : { 
 "explanation" : { 
 "type" : "string" 
 }, 
 "output" : { 
 "type" : "string" 
 } 
 }, 
 "required" : [ 
 "explanation" , 
 "output" 
 ], 
 "additionalProperties" : false 
 } 
 }, 
 "required" : [ 
 "steps" , 
 "final_answer" 
 ], 
 "additionalProperties" : false 
 } 

 Recursive schemas are supported

 Sample recursive schema using # to indicate root recursion.

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 { 
 "name" : "ui" , 
 "description" : "Dynamically generated UI" , 
 "strict" : true , 
 "schema" : { 
 "type" : "object" , 
 "properties" : { 
 "type" : { 
 "type" : "string" , 
 "description" : "The type of the UI component" , 
 "enum" : [ "div" , "button" , "header" , "section" , "field" , "form" ] 
 }, 
 "label" : { 
 "type" : "string" , 
 "description" : "The label of the UI component, used for buttons or form fields" 
 }, 
 "children" : { 
 "type" : "array" , 
 "description" : "Nested UI components" , 
 "items" : { 
 "$ref" : "#" 
 } 
 }, 
 "attributes" : { 
 "type" : "array" , 
 "description" : "Arbitrary attributes for the UI component, suitable for any element" , 
 "items" : { 
 "type" : "object" , 
 "properties" : { 
 "name" : { 
 "type" : "string" , 
 "description" : "The name of the attribute, for example onClick or className" 
 }, 
 "value" : { 
 "type" : "string" , 
 "description" : "The value of the attribute" 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ "name" , "value" ] 
 } 
 } 
 }, 
 "required" : [ "type" , "label" , "children" , "attributes" ], 
 "additionalProperties" : false 
 } 
 } 

 Sample recursive schema using explicit recursion:

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 { 
 "type" : "object" , 
 "properties" : { 
 "linked_list" : { 
 "$ref" : "#/$defs/linked_list_node" 
 } 
 }, 
 "$defs" : { 
 "linked_list_node" : { 
 "type" : "object" , 
 "properties" : { 
 "value" : { 
 "type" : "number" 
 }, 
 "next" : { 
 "anyOf" : [ 
 { 
 "$ref" : "#/$defs/linked_list_node" 
 }, 
 { 
 "type" : "null" 
 } 
 ] 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ 
 "next" , 
 "value" 
 ] 
 } 
 }, 
 "additionalProperties" : false , 
 "required" : [ 
 "linked_list" 
 ] 
 } 

 JSON mode 

 JSON mode is a more basic version of the Structured Outputs feature. While
JSON mode ensures that model output is valid JSON, Structured Outputs reliably
matches the model’s output to the schema you specify. We recommend you use
Structured Outputs if it is supported for your use case.

 When JSON mode is turned on, the model’s output is ensured to be valid JSON, except for in some edge cases that you should detect and handle appropriately.

 To turn on JSON mode with the Chat Completions, set the response_format to { "type": "json_object" } . If you are using function calling, JSON mode is always turned on.

 To turn on JSON mode with the Responses API you can set the text.format to { "type": "json_object" } . If you are using function calling, JSON mode is always turned on.

 Important notes:

 When using JSON mode, you must always instruct the model to produce JSON via some message in the conversation, for example via your system message. If you don’t include an explicit instruction to generate JSON, the model may generate an unending stream of whitespace and the request may run continually until it reaches the token limit. To help ensure you don’t forget, the API will throw an error if the string “JSON” does not appear somewhere in the context.

 JSON mode will not guarantee the output matches any specific schema, only that it is valid and parses without errors. You should use Structured Outputs to ensure it matches your schema, or if that is not possible, you should use a validation library and potentially retries to ensure that the output matches your desired schema.

 Your application must detect and handle the edge cases that can result in the model output not being a complete JSON object (see below)

 Handling edge cases 
 Python 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 
 48 
 49 
 50 
 51 
 52 const we_did_not_specify_stop_tokens = true; 
 
 try { 
 const response = await openai.chat.completions.create({ 
 model: "gpt-6-astra", 
 messages: [ 
 { 
 role: "system", 
 content: "You are a helpful assistant designed to output JSON.", 
 }, 
 { 
 role: "user", 
 content: 
 "Who won the world series in 2020? Please respond in the format {winner: ...}", 
 }, 
 ], 
 store: true, 
 response_format: { type: "json_object" }, 
 }); 
 
 // Check if the conversation was too long for the context window, resulting in incomplete JSON 
 if (response.choices[0].finish_reason === "length") { 
 // your code should handle this error case 
 } 
 
 // Check if the OpenAI safety system refused the request and generated a refusal instead 
 if (response.choices[0].message.refusal) { 
 // your code should handle this error case 
 // In this case, the .content field will contain the explanation (if any) that the model generated for why it is refusing 
 console.log(response.choices[0].message.refusal); 
 } 
 
 // Check if the model's output included restricted content, so the generation of JSON was halted and may be partial 
 if (response.choices[0].finish_reason === "content_filter") { 
 // your code should handle this error case 
 } 
 
 if (response.choices[0].finish_reason === "stop") { 
 // In this case the model has either successfully finished generating the JSON object according to your schema, or the model generated one of the tokens you provided as a "stop token" 
 
 if (we_did_not_specify_stop_tokens) { 
 // If you didn't specify any stop tokens, then the generation is complete and the content key will contain the serialized JSON object 
 // This will parse successfully and should now contain {"winner": "Los Angeles Dodgers"} 
 console.log(JSON.parse(response.choices[0].message.content)); 
 } else { 
 // Check if the response.choices[0].message.content ends with one of your stop tokens and handle appropriately 
 } 
 } 
 } catch (e) { 
 // Your code should handle errors here, for example a network error calling the API 
 console.error(e); 
 } 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 we_did_not_specify_stop_tokens = True 
 
 try : 
 response = client.chat.completions.create( 
 model = "gpt-6-astra" , 
 messages = [ 
 { 
 "role" : "system" , 
 "content" : "You are a helpful assistant designed to output JSON." , 
 }, 
 { 
 "role" : "user" , 
 "content" : 'Who won the World Series in 2020? Respond as {"winner": "team name"}.' , 
 }, 
 ], 
 response_format = { "type" : "json_object" }, 
 ) 
 
 # Check if the conversation was too long for the context window, resulting in incomplete JSON 
 if response.choices[ 0 ].finish_reason == "length" : 
 raise RuntimeError ( "The response was truncated before the JSON completed." ) 
 
 # Check if the OpenAI safety system refused the request and generated a refusal instead 
 if response.choices[ 0 ].message.refusal: 
 # your code should handle this error case 
 # In this case, the .content field will contain the explanation (if any) that the model generated for why it is refusing 
 print (response.choices[ 0 ].message.refusal) 
 
 # Check if the model's output included restricted content, so the generation of JSON was halted and may be partial 
 if response.choices[ 0 ].finish_reason == "content_filter" : 
 raise RuntimeError ( "The response was interrupted by the content filter." ) 
 
 if response.choices[ 0 ].finish_reason == "stop" : 
 # In this case the model has either successfully finished generating the JSON object according to your schema, or the model generated one of the tokens you provided as a "stop token" 
 
 if we_did_not_specify_stop_tokens: 
 # If you didn't specify any stop tokens, then the generation is complete and the content key will contain the serialized JSON object 
 # This will parse successfully and should now contain "{"winner": "Los Angeles Dodgers"}" 
 print (response.choices[ 0 ].message.content) 
 except Exception as e: 
 # Your code should handle errors here, for example a network error calling the API 
 print (e) 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 package main 
 
 import ( 
 "context" 
 "encoding/json" 
 "fmt" 
 
 "github.com/openai/openai-go/v3" 
 "github.com/openai/openai-go/v3/shared" 
 ) 
 
 func main() { 
 client := openai.NewClient() 
 completion, err := client.Chat.Completions.New(context.Background(), openai.ChatCompletionNewParams{ 
 Model: "gpt-6-astra", 
 Messages: []openai.ChatCompletionMessageParamUnion{ 
 openai.SystemMessage("You are a helpful assistant designed to output JSON."), 
 openai.UserMessage("Who won the world series in 2020? Please respond in the format {winner: ...}"), 
 }, 
 ResponseFormat: openai.ChatCompletionNewParamsResponseFormatUnion{ 
 OfJSONObject: &shared.ResponseFormatJSONObjectParam{}, 
 }, 
 }) 
 if err != nil { 
 panic(err) 
 } 
 
 choice := completion.Choices[0] 
 if choice.FinishReason == "length" || choice.FinishReason == "content_filter" { 
 fmt.Println("The JSON response is incomplete.") 
 return 
 } 
 if choice.Message.Refusal != "" { 
 fmt.Println(choice.Message.Refusal) 
 return 
 } 
 if choice.FinishReason == "stop" { 
 var value map[string]any 
 if err := json.Unmarshal([]byte(choice.Message.Content), &value); err != nil { 
 panic(err) 
 } 
 fmt.Println(value) 
 } 
 } 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 import com.fasterxml.jackson.databind.ObjectMapper; 
 import com.openai.client.OpenAIClient; 
 import com.openai.client.okhttp.OpenAIOkHttpClient; 
 import com.openai.core.JsonValue; 
 import com.openai.models.chat.completions.ChatCompletion; 
 import com.openai.models.chat.completions.ChatCompletionCreateParams; 
 import java.io.IOException; 
 import java.util.Map; 
 
 ChatCompletionCreateParams params = 
 ChatCompletionCreateParams.builder() 
 .model("gpt-6-astra") 
 .addSystemMessage("You are a helpful assistant designed to output JSON.") 
 .addUserMessage("Who won the World Series in 2020? Respond as {winner: ...}.") 
 .putAdditionalBodyProperty( 
 "response_format", JsonValue.from(Map.of("type", "json_object"))) 
 .build(); 
 
 var choice = client.chat().completions().create(params).choices().get(0); 
 if (choice.finishReason().equals(ChatCompletion.Choice.FinishReason.LENGTH) 
 || choice.finishReason().equals(ChatCompletion.Choice.FinishReason.CONTENT_FILTER)) { 
 System.out.println("The JSON response is incomplete."); 
 } else if (choice.message().refusal().isPresent()) { 
 System.out.println(choice.message().refusal().orElseThrow()); 
 } else if (choice.finishReason().equals(ChatCompletion.Choice.FinishReason.STOP)) { 
 String content = choice.message().content().orElseThrow(); 
 System.out.println( 
 new ObjectMapper() 
 .writerWithDefaultPrettyPrinter() 
 .writeValueAsString(new ObjectMapper().readTree(content))); 
 } 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 using OpenAI.Chat; 
 
 string key = Environment.GetEnvironmentVariable("OPENAI_API_KEY")!; 
 string model = "gpt-6-astra"; 
 ChatClient client = new(model, key); 
 
 ChatCompletionOptions options = new() 
 { 
 ResponseFormat = ChatResponseFormat.CreateJsonObjectFormat(), 
 }; 
 ChatCompletion completion = await client.CompleteChatAsync( 
 [new SystemChatMessage("You are a helpful assistant designed to output JSON."), new UserChatMessage("Who won the World Series in 2020? Respond with the winner in JSON.")], 
 options 
 ); 
 
 if (completion.FinishReason == ChatFinishReason.Length) 
 { 
 Console.WriteLine("The response was truncated before the JSON completed."); 
 } 
 else if (completion.FinishReason == ChatFinishReason.ContentFilter) 
 { 
 Console.WriteLine("The response was interrupted by the content filter."); 
 } 
 else if (!string.IsNullOrEmpty(completion.Refusal)) 
 { 
 Console.WriteLine(completion.Refusal); 
 } 
 else if (completion.FinishReason == ChatFinishReason.Stop && completion.Content.Count > 0) 
 { 
 Console.WriteLine(completion.Content[0].Text); 
 } 
 else 
 { 
 throw new InvalidOperationException("The completion did not contain a JSON response."); 
 } 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 require "json" 
 require "openai" 
 
 client = OpenAI::Client.new 
 completion = client.chat.completions.create( 
 model: "gpt-6-astra", 
 messages: [ 
 { 
 role: :system, 
 content: "You are a helpful assistant designed to output JSON." 
 }, 
 { 
 role: :user, 
 content: "Who won the World Series in 2020? Respond in the format {winner: ...}." 
 } 
 ], 
 response_format: { type: :json_object } 
 ) 
 
 choice = completion.choices.fetch(0) 
 finish_reason = choice.finish_reason 
 if [ 
 OpenAI::Chat::ChatCompletion::Choice::FinishReason::LENGTH, 
 OpenAI::Chat::ChatCompletion::Choice::FinishReason::CONTENT_FILTER 
 ].include?(finish_reason) 
 warn("The JSON response is incomplete.") 
 elsif choice.message.refusal 
 puts(choice.message.refusal) 
 elsif finish_reason == OpenAI::Chat::ChatCompletion::Choice::FinishReason::STOP 
 content = choice.message.content or raise "No response content" 
 puts(JSON.pretty_generate(JSON.parse(content))) 
 end 

 Python 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 
 48 
 49 
 50 
 51 
 52 
 53 
 54 
 55 
 56 
 57 
 58 
 59 
 60 const we_did_not_specify_stop_tokens = true; 
 
 try { 
 const response = await openai.responses.create({ 
 model: "gpt-6-astra", 
 input: [ 
 { 
 role: "system", 
 content: "You are a helpful assistant designed to output JSON.", 
 }, 
 { 
 role: "user", 
 content: 
 "Who won the world series in 2020? Please respond in the format {winner: ...}", 
 }, 
 ], 
 text: { format: { type: "json_object" } }, 
 }); 
 
 const message = response.output.find((item) => item.type === "message"); 
 const messageContent = message?.content[0]; 
 
 // Check if the conversation was too long for the context window, resulting in incomplete JSON 
 if ( 
 response.status === "incomplete" && 
 response.incomplete_details.reason === "max_output_tokens" 
 ) { 
 // your code should handle this error case 
 } 
 
 // Check if the OpenAI safety system refused the request and generated a refusal instead 
 if (messageContent?.type === "refusal") { 
 // your code should handle this error case 
 // In this case, the .content field will contain the explanation (if any) that the model generated for why it is refusing 
 console.log(messageContent.refusal); 
 } 
 
 // Check if the model's output included restricted content, so the generation of JSON was halted and may be partial 
 if ( 
 response.status === "incomplete" && 
 response.incomplete_details.reason === "content_filter" 
 ) { 
 // your code should handle this error case 
 } 
 
 if (response.status === "completed") { 
 // In this case the model has either successfully finished generating the JSON object according to your schema, or the model generated one of the tokens you provided as a "stop token" 
 
 if (we_did_not_specify_stop_tokens) { 
 // If you didn't specify any stop tokens, then the generation is complete and the content key will contain the serialized JSON object 
 // This will parse successfully and should now contain {"winner": "Los Angeles Dodgers"} 
 console.log(JSON.parse(response.output_text)); 
 } else { 
 // Check if the response.output_text ends with one of your stop tokens and handle appropriately 
 } 
 } 
 } catch (e) { 
 // Your code should handle errors here, for example a network error calling the API 
 console.error(e); 
 } 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 
 48 
 49 
 50 
 51 we_did_not_specify_stop_tokens = True 
 
 try : 
 response = client.responses.create( 
 model = "gpt-6-astra" , 
 input = [ 
 { 
 "role" : "system" , 
 "content" : "You are a helpful assistant designed to output JSON." , 
 }, 
 { 
 "role" : "user" , 
 "content" : 'Who won the World Series in 2020? Respond as {"winner": "team name"}.' , 
 }, 
 ], 
 text = { "format" : { "type" : "json_object" }}, 
 ) 
 
 message = next ((item for item in response.output if item.type == "message" ), None ) 
 message_content = message.content[ 0 ] if message and message.content else None 
 
 # Check if the conversation was too long for the context window, resulting in incomplete JSON 
 if ( 
 response.status == "incomplete" 
 and response.incomplete_details.reason == "max_output_tokens" 
 ): 
 raise RuntimeError ( "The response was truncated before the JSON completed." ) 
 
 # Check if the OpenAI safety system refused the request and generated a refusal instead 
 if message_content and message_content.type == "refusal" : 
 # your code should handle this error case 
 # In this case, the .content field will contain the explanation (if any) that the model generated for why it is refusing 
 print (message_content.refusal) 
 
 # Check if the model's output included restricted content, so the generation of JSON was halted and may be partial 
 if ( 
 response.status == "incomplete" 
 and response.incomplete_details.reason == "content_filter" 
 ): 
 raise RuntimeError ( "The response was interrupted by the content filter." ) 
 
 if response.status == "completed" : 
 # In this case the model has either successfully finished generating the JSON object according to your schema, or the model generated one of the tokens you provided as a "stop token" 
 
 if we_did_not_specify_stop_tokens: 
 # If you didn't specify any stop tokens, then the generation is complete and the content key will contain the serialized JSON object 
 # This will parse successfully and should now contain "{"winner": "Los Angeles Dodgers"}" 
 print (response.output_text) 
 except Exception as e: 
 # Your code should handle errors here, for example a network error calling the API 
 print (e) 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 
 48 
 49 
 50 
 51 
 52 
 53 
 54 
 55 
 56 
 57 package main 
 
 import ( 
 "context" 
 "encoding/json" 
 "fmt" 
 
 "github.com/openai/openai-go/v3" 
 "github.com/openai/openai-go/v3/responses" 
 "github.com/openai/openai-go/v3/shared" 
 ) 
 
 func main() { 
 client := openai.NewClient() 
 response, err := client.Responses.New(context.Background(), responses.ResponseNewParams{ 
 Model: "gpt-6-astra", 
 Input: responses.ResponseNewParamsInputUnion{OfInputItemList: responses.ResponseInputParam{ 
 responses.ResponseInputItemParamOfMessage( 
 responses.ResponseInputMessageContentListParam{responses.ResponseInputContentParamOfInputText("You are a helpful assistant designed to output JSON.")}, 
 responses.EasyInputMessageRoleSystem, 
 ), 
 responses.ResponseInputItemParamOfMessage( 
 responses.ResponseInputMessageContentListParam{responses.ResponseInputContentParamOfInputText("Who won the world series in 2020? Please respond in the format {winner: ...}")}, 
 responses.EasyInputMessageRoleUser, 
 ), 
 }}, 
 Text: responses.ResponseTextConfigParam{Format: responses.ResponseFormatTextConfigUnionParam{ 
 OfJSONObject: &shared.ResponseFormatJSONObjectParam{}, 
 }}, 
 }) 
 if err != nil { 
 panic(err) 
 } 
 
 if response.Status == "incomplete" { 
 fmt.Println("The JSON response is incomplete.") 
 return 
 } 
 for _, output := range response.Output { 
 if output.Type != "message" { 
 continue 
 } 
 for _, content := range output.AsMessage().Content { 
 if content.Type == "refusal" { 
 fmt.Println(content.AsRefusal().Refusal) 
 return 
 } 
 } 
 } 
 if response.Status == "completed" { 
 var value map[string]any 
 if err := json.Unmarshal([]byte(response.OutputText()), &value); err != nil { 
 panic(err) 
 } 
 fmt.Println(value) 
 } 
 } 

 1 
 2 
 3 
 4 
 5 
 6 
 7 
 8 
 9 
 10 
 11 
 12 
 13 
 14 
 15 
 16 
 17 
 18 
 19 
 20 
 21 
 22 
 23 
 24 
 25 
 26 
 27 
 28 
 29 
 30 
 31 
 32 
 33 
 34 
 35 
 36 
 37 
 38 
 39 
 40 
 41 
 42 
 43 
 44 
 45 
 46 
 47 
 48 
 49 
 50 
 51 
 52 
 53 
 54 
 55 
 56 
 57 
 58 
 59 
 60 
 61 import com.openai.client.OpenAIClient; 
 import com.openai.client.okhttp.OpenAIOkHttpClient; 
 import com.openai.errors.OpenAIServiceException; 
 import com.openai.models.ResponseFormatJsonObject; 
 import com.openai.models.responses.EasyInputMessage; 
 import com.openai.models.responses.ResponseCreateParams; 
 import com.openai.models.responses.ResponseInputItem; 
 import com.openai.models.responses.ResponseStatus; 
 import com.openai.models.responses.ResponseTextConfig; 
 import java.util.List; 
 
 ResponseCreateParams params = 
 ResponseCreateParams.builder() 
 .model("gpt-6-astra") 
 .inputOfResponse( 
 List.of( 
 ResponseInputItem.ofEasyInputMessage( 
 EasyInputMessage.builder() 
 .role(EasyInputMessage.Role.SYSTEM) 
 .content("You are a helpful assistant designed to output JSON.") 
 .build()), 
 ResponseInputItem.ofEasyInputMessage( 
 EasyInputMessage.builder() 
 .role(EasyInputMessage.Role.USER) 
 .content( 
 "Who won the World Series in 2020? Respond in the format {winner: ...}.") 
 .build()))) 
 .text( 
 ResponseTextConfig.builder() 
 .format(ResponseFormatJsonObject.builder().build()) 
 .build()) 
 .build(); 
 
 try { 
 var response = client.responses().create(params); 
 if (response.status().filter(ResponseStatus.INCOMPLETE::equals).isPresent()) { 
 String reason = 
 response 
 .incompleteDetails() 
 .flatMap(details -> details.reason()) 
 .map(Object::toString) 
 .orElse("unknown"); 
 System.out.println("The JSON response is incomplete. Reas