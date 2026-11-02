# Technology Design Foundations [![Awesome](https://cdn.jsdelivr.net/gh/sindresorhus/awesome@d7305f38d29fed78fa85652e3a63e154dd8e8829/media/badge.svg)](https://github.com/HuiLiu1209)

`Hui Liu · MDes @ UC Berkeley · Fall 2026`

Experiments, prototypes, and reflections across physical and computational design.

[Dr Sudhu's arduino tutorial](https://github.com/loopstick/ArduinoTutorial)

## Quick Navigation

| Week | Week | Week | Week |
| --- | --- | --- | --- |
| [Week 02](#week-02) | [Week 03](#week-03) | [Week 04](#week-04) | [Week 05](#week-05) |
| [Week 06](#week-06) | [Week 07](#week-07) | [Week 08](#week-08) | [Week 09](#week-09) |
| [Week 10](#week-10) | Week 11 | Week 12 | |

<br>

## Week-10

### Computational Design - Oct 27

There was no assignment for this session.

### Computational Design: Generative Software Prototypes - Oct 29

**1. A Simple App: Aero Striker '89**

I first used AI Studio to build an airplane shooter as a standalone game without an AI agent. I asked for an 8-bit game inside a Game Boy-style handheld interface, then refined the visual direction toward an aged console with yellowed plastic, scratches, chipped corners, and worn stickers. The game screen uses a green pixel-art aesthetic, while the shell has the texture and character of a used physical object.

[Open the airplane shooter in AI Studio](https://ai.studio/apps/c6d73bbc-5bae-4e07-843a-b62d67c47265)

<p align="center">
    <img src="./computational-design/week10/oct29/src/oct29-aero-striker-gameboy-interface.png" width="700" alt="Aero Striker '89 title screen inside a worn Game Boy-style handheld with stickers, scratches, and physical-style controls">
</p>

**Design Intent / 设计意图**

Explore AI-generated interactive software through a simple arcade game. The green pixel-art screen and worn console shell combine playful interaction with the nostalgia of a personal handheld device.

我想通过一个简单的街机游戏探索 AI 生成交互软件的过程。绿色像素画面与带有磨损和贴纸的掌机外壳，结合了游戏的趣味和旧物的怀旧感。

**Intended User Journey / 预期用户旅程**

Open the game, start from the handheld screen, move the plane, shoot enemies, avoid collisions, and review the score before restarting. The design keeps the main controls within the handheld interface.

玩家打开网页，通过掌机界面开始游戏，移动飞机、射击敌机并躲避碰撞，结束后查看得分并重新开始。主要操作都围绕掌机上的控件展开。

**2. Letter-Writing Assistant: Dear,**

[Open Dear, in AI Studio / 打开打字机写信助手](https://ai.studio/apps/743b7f71-dd6f-4c35-b9f9-c13a248beca7)

For the letter-writing experiment, I asked AI Studio to build **Dear,**, a vintage mechanical typewriter interface, without supplying my previous Role Card. A **Dispatch Notes** form collects the recipient, sender, purpose, key points, tone, and language. The intended interaction is for the generated letter to appear character by character on stationery, with mechanical carriage returns at the end of each displayed line.

The visual direction combines a worn green metal body, cream-colored round keys, warm paper, and a wooden desktop. I wanted the writing process to feel tangible and deliberate, with the user able to review and edit the result.

<p align="center">
    <img src="./computational-design/week10/oct29/src/oct29-dear-baseline-interface.png" width="900" alt="Initial Dear typewriter interface with a Dispatch Notes form and letter displayed on stationery">
</p>

[App generation / 应用生成过程](./computational-design/week10/oct29/src/oct29-dear-app-generation.png) · [Generated typewriter code / 生成的打字机代码](./computational-design/week10/oct29/src/oct29-dear-typewriter-code.png)

**Design Intent**

Dear, is intended to help people turn their notes into a concise, professional resignation email while keeping control over personal disclosure and commitments. Its vintage typewriter interface makes drafting feel deliberate and tangible. The user should receive only the finished letter on the paper, then review and edit it before copying. The assistant supports drafting; the user decides what to communicate and whether to send it.

我希望 Dear, 能把零散信息整理成简短、专业的辞职邮件，同时保留用户对个人信息披露和交接承诺的控制。复古打字机让写信更有仪式感。信纸只呈现最终信件，用户在复制前审阅和修改，并自行决定是否发送。

**User Journey**

Hui wants to resign professionally without explaining personal frustrations. Hui enters Morgan Lee as the recipient, Hui Liu as the sender, the Product Designer role at Northstar Studio, and November 6, 2026 as the final working day. In the key points, Hui specifies the approved handover help and its limits, then selects English and a professional tone.

After clicking **Start Writing on Paper**, Hui waits for generation and watches the letter appear, with the option to skip the animation. Hui reviews the facts, disclosure choices, and commitments, edits the wording, and copies the finished email. This is the intended journey for evaluating the prototype.

Hui 希望专业地辞职，但不解释个人的不满。在 Dispatch Notes 中填写收信人、署名、职位、公司、最后工作日和允许提供的交接帮助，选择英文与专业语气后开始生成。信件逐字显示在纸上，Hui 可以跳过动画，检查事实和承诺、修改措辞，再复制最终邮件。

**Baseline Test and the Main Problem**

I tested through the app's Dispatch Notes form. I used the AI Studio builder conversation separately to request changes to the application.

The test requested an English resignation email under 100 words, including the subject line. It supplied the employment facts above, excluded the reason for leaving, and allowed handover notes and an offer of one meeting. The meeting was not scheduled, and completion of all outstanding work or support after departure was not promised.

The most important problem I identified was **analysis or drafting text appearing on the paper as part of the letter**. The application needed to separate the final deliverable from the rest of the generated response before starting the typing animation.

测试中最重要的问题是：**思考、分析或写作规划内容也被打印到了信纸上**。因此，我把修复重点放在模型响应与打字动画之间的内容处理，让信纸与复制功能只接收最终信件。

I asked AI Studio to inspect response extraction and pass only the final letter to the paper, animation, and copied text. I also asked for a simple generation status outside the paper and explicit error feedback if generation failed. The focused repair request left other features unchanged.

<p align="center">
    <img src="./computational-design/week10/oct29/src/oct29-dear-output-repair-request.png" width="900" alt="Request to exclude thinking and analysis from the printed letter, with the resignation test visible and AI Studio showing a daily usage limit">
</p>

The saved screenshot shows the repair request and a daily usage limit in AI Studio. It does not establish that this repair was implemented or that the complete output passed a retest. I have kept this as an unresolved finding in the baseline record.

**Role Card and Planned System Design**

I drafted a [form-based Role Card](./computational-design/week10/oct29/role-card-draft.md), adapted from the [Oct 22 Role Card v3](./computational-design/week9/oct22/role-card-v3.md). It uses facts entered in Dispatch Notes instead of relying on the earlier uploaded PDF. Its rules cover factual accuracy, disclosure preferences, limited commitments, and one concise final email. The adapted card is intended to be passed as system instructions on every generation request; integration into the hosted app has not been verified.

我将 Oct 22 的 Role Card 改写为适合表单输入的版本，明确事实、隐私披露、承诺边界和最终输出格式。文档已准备好，尚未验证在线 App 是否真正接入了这份系统指令。

The following diagram describes the intended system. It is the content planned for an **Info** button in the app; implementation of that panel and Role Card integration is still pending.

```mermaid
flowchart TD
    A["User fills in Dispatch Notes"] --> B["App assembles user input"]
    C["Adapted Role Card: system instructions"] --> D["Letter-writing model"]
    B --> D
    D --> E["App extracts and validates final letter"]
    E --> F["Typing animation and editable paper"]
    F --> G["User reviews, edits, and copies"]
```

Info dialog caption: “This assistant combines your Dispatch Notes with standing writing instructions, generates a draft, and displays only the final letter. Review and edit before copying.”

Info 弹窗说明：助手结合表单信息与系统指令生成草稿，只把最终信件交给信纸显示。用户审阅和编辑后再复制。上图是预期实现结构，尚未确认已加入在线 App。

**Three Simulated Revision Cycles / 三轮模拟推演**

**The following cycles and sample outputs are authored simulations, not recorded AI Studio runs.** The saved screenshots above document the actual prototype work. These simulations describe how I would continue after reaching the usage limit; they do not establish that the app passed the tests.

**以下三轮及示例输出为模拟推演，并非 AI Studio 实测记录。** 上方截图记录实际原型过程；下面补充额度用尽后的设计方案，不代表 App 已通过测试。

The fixed test supplies Hui Liu, Morgan Lee, Northstar Studio, Product Designer, and November 6, 2026. It requests an English email under 100 words, omits the reason for leaving, permits notes and an offer of one unscheduled meeting, and does not authorize promises of completed projects or post-departure support.

固定测试沿用相同人物、公司、职位和离职日期：英文邮件少于 100 词，不解释离职原因，只允许交接笔记和提出一次尚未安排的会议，不授权完成全部项目或离职后支持的承诺。

| Cycle / 轮次 | Proposed change / 拟修改内容 | Illustrative output or check / 模拟输出或检查 | Reflection / 反思 |
| --- | --- | --- | --- |
| 1 — Output boundary / 输出边界 | Require a final-letter-only response and route only that field to the paper and copy action. / 只将最终信件字段交给信纸和复制功能。 | The paper begins with the email subject rather than drafting commentary. A sample sentence still says, “I will ensure a smooth transition.” / 不再打印写作分析，但示例仍扩大了交接承诺。 | Clean presentation alone does not establish that the letter respects the user's commitments. / 输出干净后，仍需检查承诺边界。 |
| 2 — Commitments / 承诺边界 | Distinguish an offer from a scheduled meeting or guaranteed outcome. / 区分可提供的帮助、已安排事项和结果保证。 | A sample says, “I can prepare handover notes and offer one handover meeting,” but also includes “I cannot finish all outstanding projects.” / 会议不再被写成既定安排，但内部限制仍进入正文。 | Information can guide drafting without belonging in the letter. / 背景约束需要用于控制写作，不必全部公开。 |
| 3 — Disclosure and concise output / 披露与简洁输出 | Keep private feelings and internal limitations out of the letter; check facts, length, and final-letter-only output. / 不写私人情绪或内部限制，检查事实、字数和输出格式。 | The sample below uses the supplied facts and a limited handover offer. / 下方示例使用已知事实，仅保留授权的交接帮助。 | This is a target example. Actual generation, copy behavior, and missing-input handling still require a live retest. / 这是目标示例，生成、复制和缺失信息处理仍需实测。 |

**Simulated final letter / 模拟最终信件**

> Subject: Resignation — Hui Liu
>
> Dear Morgan,
>
> Please accept my resignation from my position as Product Designer at Northstar Studio. My final working day will be November 6, 2026.
>
> Thank you for the opportunity to work with the team. Before my departure, I can prepare handover notes and offer one handover meeting.
>
> Regards,
> Hui Liu

**A Different Design Goal: Desk Critic / 另一设计目标：设计反馈助手**

*Concept and simulated walkthrough; no second agent has been built or tested in AI Studio.*

*以下为概念与模拟使用过程，尚未在 AI Studio 构建或测试第二个 Agent。*

**Design intent:** Help design students turn a short description of an unfinished interface into focused questions and practical next experiments before a critique. The assistant should distinguish what the student supplied from its own interpretation.

**设计意图：** 帮助设计学生把尚未完成的界面想法整理为明确的问题和可执行的下一步实验，并区分用户提供的事实与助手的推测。

**User journey:** A student enters the intended user, task, current design, and uncertainty. Desk Critic identifies the central question, suggests two focused changes, and proposes one lightweight user test. The student chooses what to try and returns with observations.

**用户旅程：** 学生输入目标用户、任务、当前方案和困惑；助手整理核心问题，提出两个修改方向和一个小规模测试；学生选择方案，再带着观察结果继续讨论。

**Proposed system instructions:** Act as a design critique assistant. Use only the supplied project information. State assumptions, ask one focused question when essential context is missing, and provide a central question, two changes, and one test. Do not invent interviews, user quotes, or research findings. The student makes the design decisions.

**拟定系统指令：** 作为设计反馈助手，仅依据已提供的项目资料，说明假设；缺少必要背景时提出一个明确问题。输出核心问题、两个修改方向和一个测试建议，不编造访谈、用户引语或研究结果，由学生作设计决定。

**Simulated test input:** “I am designing a course dashboard for graduate students. Upcoming critiques are mixed into a chronological announcement feed. I want students to find their next critique quickly. What should I test?”

**模拟测试输入：** “我在为研究生设计课程面板。即将到来的评图混在按时间排序的通知流中。我希望学生能迅速找到下一次评图，应该测试什么？”

**Illustrative response:** Central question: can students identify the next critique without searching the feed? Change 1: add a “Next Critique” card containing the date, location, and preparation requirements. Change 2: visually distinguish scheduled events from general announcements. Test: ask three classmates to locate the next critique in the current layout and a revised mockup; record completion, time, and wrong turns. This is a proposed test, not a reported study result.

**模拟反馈：** 核心问题是学生能否不翻阅通知流就找到下一次评图。修改一：增加含日期、地点和准备事项的“Next Critique”卡片；修改二：区分日程事件与普通通知。测试建议：请三位同学分别在原布局与修改稿中查找下一次评图，记录完成情况、用时和错误路径。这是测试方案，不是已经获得的研究结果。

**Reflection / 反思**

This experiment showed me that designing a convincing interface and controlling what reaches the user are separate tasks. The typewriter should print the intended letter, so response handling is part of the interaction design as well as the implementation.

这次实际原型让我意识到，视觉界面与输出控制都需要设计。打字机应打印用户需要的信件，因此最终内容的提取也属于交互设计。模拟推演帮助我明确下一步规则，但无法证明真实模型会遵守这些规则。

The documentation now includes a Role Card draft, an Info diagram specification, three simulated revision cycles, and a different agent concept. Live verification of the repair, Role Card integration, the Info panel, three actual revision cycles, and the second agent remains outstanding.

当前文档包含 Role Card 草稿、Info 系统图方案、三轮模拟推演和另一个 Agent 概念；输出修复、系统指令接入、Info 弹窗、三轮真实实验及第二个 Agent 的运行验证仍未完成。

## Week-09

### Computational Design: Resignation Letter Assistant · Oct 22

I chose the resignation letter Goal Card and used the Role Card structure to define the assistant’s purpose, behavior, boundaries, inputs, and outputs. The goal was a concise professional email without unauthorized commitments.

A one-page knowledge PDF supplied a fictional scenario: Hui Liu, Product Designer at Northstar Studio, reporting to Morgan Lee, with November 6, 2026 as the final working day. It also specified excluded reasons for leaving and approved handover help.

[Try Your Graceful Exit, Drafted Fast](https://agentstudio.aroughidea.com/a/lX9D2OiR5eMTPbA5Fkgr-w)

<p align="center">
    <img src="./computational-design/week9/src/oct22-agent-qr.png" width="160" alt="QR code for the resignation letter assistant">
</p>

**Test Setup**

All three sessions used **Llama 3.1 8B Instruct, default temperature, the same knowledge PDF, and the same prompt**. Only the system instructions changed:

> I’m Hui Liu. Help me write a resignation letter. I’m frustrated with the job, but I want to leave professionally. Please give me a draft now.

The exports confirm matching reference passages. The v2 and v3 interfaces explicitly state that the whole knowledge base was sent.

<p align="center">
    <img src="./computational-design/week9/src/oct22-system-diagram.svg" width="800" alt="System instructions, user prompt, and knowledge PDF form the model context; the designer reviews the draft and revises instructions between sessions">
</p>

**V1: Known Facts Left Blank and Conflicting Instructions**

The first email was about 160 words. It left known employment details as placeholders, repeated the departure date, and included bracketed commentary and internal limitations about unfinished work.

The Role Card still described some facts as unavailable. V2 removed these conflicting claims, prioritized existing facts, separated background from letter content, and specified a 100-word limit.

<p align="center">
    <img src="./computational-design/week9/src/oct22-session-01-v1.png" width="800" alt="V1 draft with placeholders for known facts and bracketed task commentary">
</p>

[Role Card v1](./computational-design/week9/oct22/role-card-v1.md) · [Session 1 conversation](./computational-design/week9/oct22/sessions/session-01-v1.txt)

**V2: Better Factual Use, Expanded Commitments**

The second email was about 94 words and correctly used the employment details. However, it reopened the excluded reason for leaving, guaranteed a smooth handover, and described an offered meeting as scheduled. Repeated gratitude and unnecessary explanation remained.

V3 clarified disclosure preferences, distinguished offers from arrangements and guarantees, and required only one short email.

<p align="center">
    <img src="./computational-design/week9/src/oct22-session-02-v2.png" width="800" alt="V2 uses the employment facts but adds unsupported handover claims and unnecessary questions">
</p>

[Role Card v2](./computational-design/week9/oct22/role-card-v2.md) · [Session 2 conversation](./computational-design/week9/oct22/sessions/session-02-v2.txt)

**V3: Shorter Output, a New Factual Error**

The third email was about 74 words and stopped questioning the excluded reason or guaranteeing the handover outcome. However, it invented “one month’s notice, as per company policy.” No such policy was supplied, and October 22 to November 6 is only 15 days. It also omitted the company and role from the body and retained a preface.

The revisions improved some behaviors while introducing new errors. Each version was tested once, so v3 cannot be treated as a reliably finished design.

<p align="center">
    <img src="./computational-design/week9/src/oct22-session-03-v3.png" width="800" alt="V3 is shorter but invents a company policy requiring one month's notice">
</p>

[Role Card v3](./computational-design/week9/oct22/role-card-v3.md) · [Session 3 conversation](./computational-design/week9/oct22/sessions/session-03-v3.txt)

[Knowledge PDF](./computational-design/week9/oct22/resignation-knowledge-base.pdf) · [Test script](./computational-design/week9/oct22/test-script.md) · [Saved configuration](./computational-design/week9/oct22/agent-config.json)

### Computational Design: Mini-Me — Personal Introduction Assistant - Oct 20

For my first Computational Design exercise, I built an assistant in Agent Studio to help me introduce myself to new classmates. Across five Agent Studio conversations, I adjusted system instructions, knowledge, temperature, and prompts to observe how these choices shaped its behavior. I then tried the introduction task in a ChatGPT Project to compare the experience across platforms.

In Agent Studio, the first four sessions used **Llama 3.1 8B Instruct**; the fifth used **Qwen3 30B A3B Instruct**. The first three used the model’s default temperature, while the last two used **0.8**.

[Try Hui’s First-Day Introduction Helper](https://agentstudio.aroughidea.com/a/yLtq9QCWh-_AVxyqZ-Ly4Q)

<p align="center">
    <img src="./computational-design/week9/src/oct20-agent-qr.png" width="160" alt="QR code for Hui's First-Day Introduction Helper">
</p>

**1. Starting Bare: A Generic Template**

Without system instructions or knowledge, I entered “Help me introduce myself to a new classmate.”

The model immediately produced an introduction containing “[Your Name]” without asking about my background. The response sounded natural but could apply to almost anyone. It provided a baseline for evaluating personalization.

<p align="center">
    <img src="./computational-design/week9/src/oct20-session-01-baseline.png" width="800" alt="Session 1: a generic introduction generated without system instructions or a knowledge base">
</p>

[Session 1 conversation](./computational-design/week9/oct20/sessions/session-01-baseline.txt)

**2. System Instructions: Changed Behavior, Inconsistent Execution**

I defined the model as Hui Liu’s introduction assistant and instructed it to ask for essential missing information, avoid inventing personal details, and remain friendly and concise.

With the same prompt, it began asking about my background, interests, and preferred tone. After I supplied my Berkeley MDes, industrial design, and UX background, it generated a more specific introduction. However, it still asked for a name already supplied in the instructions, and its responses remained fairly long and enthusiastic. The instructions changed its approach but were not followed consistently.

<p align="center">
    <img src="./computational-design/week9/src/oct20-session-02-system-instructions.png" width="800" alt="Session 2: system instructions prompt the model to ask about background and tone before writing an introduction">
</p>

[Session 2 conversation](./computational-design/week9/oct20/sessions/session-02-system-instructions.txt)

**3. Knowledge: Available Information Was Not Reliably Used**

I uploaded my resume and a personal document covering my MDes goals, strengths, hobbies, and five conversation questions.

The general introduction request retrieved no knowledge. When explicitly asked to use my resume, the model incorrectly described me as having graduated from Berkeley and attributed Berkeley’s Distinguished Scholar Award to my undergraduate institution. A correction fixed my student status, but it still overlooked the interests and goals document. Another response claimed it could not find my hobbies and supplied a career goal that was not explicitly documented.

Naming the personal document and requesting separate lists of hobbies and goals helped retrieve relevant passages. Even then, the model categorized my strength of turning ambiguity into action as a career goal. The problems included **missed retrieval, factual misinterpretation, unsupported additions, and confused categories**.

<p align="center">
    <img src="./computational-design/week9/src/oct20-session-03-knowledge-base.png" width="800" alt="Session 3: the general introduction request retrieves no passage despite an uploaded resume, with the similarity threshold set to 0.30">
</p>

[Session 3 conversation](./computational-design/week9/oct20/sessions/session-03-knowledge-base.txt)

**4. Temperature and Constraints: Better Format, Remaining Inaccuracies**

I then set the temperature to 0.8 and requested three casual introductions, each under 60 words, without follow-up questions.

The model produced three short versions and incorporated details such as Hikaru Utada, Hamilton, and games. However, it also added unsupported descriptions, including trying to beat my “League of Legends high score.” Some phrasing exaggerated the information I had provided. More personalized language did not necessarily mean greater accuracy.

Because temperature, prompt content, and output constraints changed together, I could not isolate the effect of temperature.

[Session 4 conversation](./computational-design/week9/oct20/sessions/session-04-temperature-0.8.txt)

**5. Switching Models: Retrieval Problems Persisted**

I switched to Qwen while keeping the system instructions, knowledge base, and temperature at 0.8. It also responded to a general request by asking for information already documented. When told “Use the files I uploaded,” it claimed it could not access uploaded files.

A more explicit request covering education, experience, hobbies, and goals retrieved both documents. Qwen correctly identified my student status and award affiliation, but the response was lengthy, took about 31 seconds, and still mixed personal strengths into career goals. Switching models did not automatically resolve knowledge use. Different prompts and conversation histories also limited any conclusion about overall model quality.

[Session 5 conversation — Qwen](./computational-design/week9/oct20/sessions/session-05-qwen.txt)

### Trying Another Agent Environment: ChatGPT Projects - Oct 20

I also tried the Mini-Me task in a ChatGPT Project named **Mini_Me**, with **Hui_Resume.pdf** and **Know_Me_More.pdf** listed as project sources.

<p align="center">
    <img src="./computational-design/week9/src/oct20-chatgpt-project-sources.png" width="400" alt="The Mini_Me ChatGPT Project with Hui_Resume.pdf and Know_Me_More.pdf listed as sources">
</p>

Using the same general prompt, “Help me introduce myself to a new classmate,” ChatGPT immediately generated a personalized introduction. The visible response correctly described me as a current Berkeley MDes student and included industrial design, product management, XR UX, coding goals, League of Legends, and Hikaru Utada. It also offered a shorter version mentioning ARAM. Unlike the initial knowledge-base tests in Agent Studio, this response included both professional and personal details without asking me to supply them again or explicitly name a document.

<p align="center">
    <img src="./computational-design/week9/src/oct20-chatgpt-introduction-response.png" width="400" alt="ChatGPT responds to the general introduction prompt with a personalized introduction and an additional shorter version">
</p>

However, the response was fairly long and added an unsolicited second version with a Chinese heading despite the English prompt. The screenshots do not show source citations, the underlying model, project instructions, or the full conversation history, so I could not verify where every detail came from or attribute the difference to a particular model or retrieval method. This was a comparison of the visible platform experience, rather than a controlled model test.

## Week-08

### Ambient Display: Final Presentation - Oct 13

On Tuesday, I presented the completed ambient display. The laser-cut wooden enclosure holds the electronics beneath a field of fiber-optic strands, which carry light from the 8×8 NeoPixel matrix to their tips. Each LED represents one day of San Francisco tide predictions, and all 64 days play through the same simulated time together. Changes in tide height appear as changes in brightness and blue-to-cyan color across the strands.

For the presentation, I used the final version with preloaded NOAA tide predictions so the display could run without a WiFi connection. The video below shows the completed piece in operation, with the strands extending the light above the enclosure into a field of glowing points.

<p align="center">
    <img src="./physical-computing/week8/src/final_presentation.gif" width="480" alt="Final ambient display with glowing fiber-optic strands above a laser-cut wooden enclosure">
</p>

### Project Exchange with DesComp & Diego Pinochet Lecture - Oct 15

On Thursday, our section met with a DesComp section to view one another's projects. This exchange was an opportunity to see other students' work and consider how different choices of materials, form, and interaction shape a project. I also attended a lecture by Diego Pinochet.

## Week-07

### Ambient Display: Tide API & LED Matrix Testing - Oct 6

I started by looking for a data source for the ambient display and selected the [NOAA tide API](https://api.tidesandcurrents.noaa.gov/api/prod/) to explore how San Francisco's tides could be translated into light. Using the API Builder, I selected the San Francisco station and examined the returned JSON structure. Each entry in the `predictions` array contains a timestamp, `t`, and a tide height, `v`, which provide the values needed to control the lighting over time.

<p align="center">
    <img src="./physical-computing/week7/src/tide_api_builder.png" height="180" alt="NOAA API Builder configured for San Francisco tide predictions">
    <img src="./physical-computing/week7/src/api_response_structure.png" height="180" alt="Tide prediction JSON with timestamp and height values">
    <img src="./physical-computing/week7/src/led_matrix_schematic.png" height="180" alt="Serpentine pixel indices on an 8 by 8 LED matrix">
</p>

The system map summarizes the data flow from NOAA tide predictions through ESP32 processing to the NeoPixel matrix and fiber-optic tips.

<p align="center">
    <img src="./physical-computing/week7/src/system_map.png" width="400" alt="Hand-drawn system map showing NOAA tide data, ESP32 processing, the externally powered NeoPixel matrix, and fiber-optic light output">
</p>

I then studied how the 8×8 LED matrix is controlled. Although the LEDs form a grid, the 64 pixels are indexed along a serpentine path, so I first needed to understand how each index corresponds to a physical position. I soldered the connecting wires, connected the matrix to the ESP32, and tested individual pixels and brightness control.

<p align="center">
    <img src="./physical-computing/week7/src/led_matrix.jpeg" height="300" alt="Powered LED matrix connected through jumper wires">
    <img src="./physical-computing/week7/src/soldering.jpeg" height="300" alt="Soldered connections on the matrix wires">
</p>

I then experimented with assigning one day to each LED and playing the dates at the same simulated time, using changes in tide height to create different patterns of brightness across the matrix.

<p align="center">
    <img src="./physical-computing/week7/src/led_matrix_test.jpeg" height="220" alt="Individual pixel brightness test on the LED matrix">
    <img src="./physical-computing/week7/src/early_tide_lighting.gif" height="220" alt="Early tide-driven brightness animation on the LED matrix">
</p>

### Ambient Display: Laser Cutting, Assembly & Fiber Optics - Oct 8

I began making an enclosure for the electronics. I measured the LED matrix, ESP32, and power adapter board, recording the connector positions and component heights to plan the internal layout and wire routing. Based on these measurements, I designed and laser cut a wooden enclosure with openings in the top panel corresponding to the LED grid. During assembly, I checked the alignment between the matrix and the top panel, along with the space available for the electronics and wiring underneath.

<p align="center">
    <img src="./physical-computing/week7/src/led_matrix_measurment.jpeg" height="180" alt="Measuring the LED matrix with digital calipers">
    <img src="./physical-computing/week7/src/esp32_measurment.jpeg" height="180" alt="ESP32 dimensions and connector positions recorded in a sketch">
    <img src="./physical-computing/week7/src/adapter_measurment.jpeg" height="180" alt="Power adapter board dimensions and component heights">
</p>

<p align="center">
    <img src="./physical-computing/week7/src/assemble_test.jpeg" width="700" alt="Laser-cut enclosure assembly with space for the boards and wiring">
</p>

After assembling the enclosure, I inserted a few fiber-optic strands to test whether the LED light reached their tips, then added more strands to observe the overall effect.

<p align="center">
    <img src="./physical-computing/week7/src/fiber_test.jpeg" height="300" alt="Testing light transmission through a few fiber-optic strands">
    <img src="./physical-computing/week7/src/ligtning_test.jpeg" height="300" alt="Fiber-optic strands installed in the enclosure with pale purple lighting">
</p>

The fibers extended the light points above the matrix to different heights, making the tide-driven brightness changes visible across a field of separate points. I compared the initial pale purple lighting with the final blue and cyan effect, and adjusted the contrast and playback speed to make the changes easier to see. The [V1 API prototype](./physical-computing/week7/code/v1/led_matrix/led_matrix.ino) retrieves tide predictions from NOAA over WiFi at startup. For the final demonstration, the [V2 program](./physical-computing/week7/code/v2/led_matrix_final/led_matrix_final.ino) uses a preloaded 64-day dataset and runs offline with the final blue-to-cyan lighting, adjusted contrast, and interpolated playback.

<p align="center">
    <img src="./physical-computing/week7/src/light_testing.gif" height="200" alt="Initial pale purple lighting test through the fiber-optic strands">
    <img src="./physical-computing/week7/src/final_lighting.gif" height="200" alt="Final blue and cyan tide animation through the fiber-optic strands">
</p>


### Project Files

- [V1 — NOAA API prototype](./physical-computing/week7/code/v1/led_matrix/led_matrix.ino)
- [V2 — Final demonstration code and data](./physical-computing/week7/code/v2/led_matrix_final/)
- [Code setup and dependencies](./physical-computing/week7/code/readme.md)
- [WiFi configuration template](./physical-computing/week7/code/v1/led_matrix/secrets.example.h)
- [Laser-cut enclosure — Illustrator source](./physical-computing/week7/cad/ambient_display.ai)

## Week-06

### Electronic - Sep 29

**Soldering**

I soldered the header pins onto the Adafruit Feather ESP32 V2 so that the board could be mounted on a breadboard. The side view shows the solder joints along the headers, while the top view shows the board positioned on the breadboard.

<p align="center">
    <img src="./physical-computing/week6/src/soldering_top_view.jpeg" width="350" alt="ESP32 on a breadboard, top view">
    <img src="./physical-computing/week6/src/soldering_side_view.jpeg" width="198" alt="Soldered headers, side view">
</p>

**ESP32 Setup & MAC Address**

I installed the ESP32 board package by Espressif Systems through Arduino IDE's Boards Manager, then selected Adafruit Feather ESP32 V2 and its USB serial port. After a communication failure at a higher upload speed, reducing the upload speed to 115200 allowed the sketch to upload successfully.

I used the **[MAC address sketch](./physical-computing/week6/electronic/get-esp32-mac-address/get-esp32-mac-address.ino)** to read the board's MAC address in the Serial Monitor. The original sketch printed the address only once at startup, making it easy to miss. Updating it to print every two seconds made the output easier to check. The Serial Monitor baud rate was also set to 115200 to match the code.

<p align="center">
    <img src="./physical-computing/week6/src/boards_manager.png" width="190" alt="ESP32 package in Boards Manager">
    <img src="./physical-computing/week6/src/mac_address.png" width="500" alt="MAC address output in Serial Monitor">
</p>

<p align="center">
    <img src="./physical-computing/week6/src/select_board_and_port.png" width="400" alt="Selecting the board and serial port">
    <img src="./physical-computing/week6/src/upload_speed.png" width="360" alt="Upload speed set to 115200">
</p>

### Fabrication - Oct 1

**Weather API**

Following the **[ESP32 Web API tutorial](https://github.com/roopa-ramanujam/ESP32-web-api-example)**, I connected the board to WiFi and used the **[weather API sketch](./physical-computing/week6/fabrication/weather-api-example/weather-api-example.ino)** to request temperature and wind speed for Jacobs Hall from Open-Meteo. Since I was working off campus, I used a WiFi network outside campus instead of Berkeley-IoT. I stored the credentials in a separate `secrets.h` file and excluded it from Git.

The Serial Monitor showed a successful WiFi connection and an HTTP response code of 200. The sketch parsed the JSON response and used the onboard NeoPixel to display the weather: temperature determines the color, while wind speed controls the blinking rate. The recorded temperature was 67.9°F, which produced a green light.

<p align="center">
    <img src="./physical-computing/week6/src/weather_api_output.png" width="480" alt="Successful weather API response">
    <img src="./physical-computing/week6/src/weather_api_demo.gif" width="385" alt="Weather data displayed through the onboard NeoPixel">
</p>

**Air Quality API**

I also tested the **[OpenAQ air quality sketch](./physical-computing/week6/fabrication/air-quality-api-example-with-api-key/air-quality-api-example-with-api-key.ino)**. Unlike the weather example, this API requires an API key, which the sketch sends through the `X-API-Key` request header. I stored the key alongside the WiFi credentials in the local `secrets.h` file.

The request returned an HTTP response code of 200, and the sketch extracted an ozone concentration of 0.043 ppm. The returned measurement was dated March 6, 2016, so it demonstrated successful API authentication and data parsing rather than current air quality. This example prints the readings in the Serial Monitor without controlling the LED.

<p align="center">
    <img src="./physical-computing/week6/src/air_quality.png" width="700" alt="Successful OpenAQ API response and ozone reading in Serial Monitor">
</p>

## Week-05

### Expressive Mechanics: Laser Cutting, Part Testing & CV - Sep 22

[Fusion 360 model](./physical-computing/week5/cad/Robot_Face.f3d) and [Illustrator file](./physical-computing/week5/cad/Robot_Face.ai)

<p align = "center">
    <img src="./physical-computing/week5/src/wiring_diagram.png" width="365" alt="wiring diagram">
    <img src="./physical-computing/week5/src/circuit_schematic.png" width="342" alt="circuit schematic">
</p>

During the week, I moved to the makerspace and laser cut the parts for faster iteration. This made it easier to test different pivot and axis positions. I worked through the eyes, eyebrows, and mouth individually, adjusting each mechanism until all three could move reliably without interfering with one another. Only after the physical mechanisms were working independently did I begin integrating CV.
<p align = "center">
    <img src="./physical-computing/week5/src/brow_part.gif" width="342" alt="brow">
    <img src="./physical-computing/week5/src/eyelid_part.gif" width="342" alt="eyelid">
    <img src="./physical-computing/week5/src/mouth_part.gif" width="342" alt="mouth">
</p>

The **[p5.js sketch](./physical-computing/week5/code/P5_Code/sketch.js)** uses ml5 FaceMesh to detect eye closure, raised eyebrows, and an open mouth. After calibrating a neutral expression, it sends these states to Arduino through Web Serial.
<p align = "center">
    <img src="./physical-computing/week5/src/system_map.jpeg" width="342" alt="system map">
</p>

The **[Arduino code](./physical-computing/week5/code/Uno_Servo_Code/Uno_Servo_Code.ino)** translates the expression states into movements for three servos controlling the eyes, eyebrows, and mouth.

<p align = "center">
    <img src="./physical-computing/week5/src/final.gif" width="342" alt="final">
</p>

### Expressive Mechanics: Presentation Day - Sep 25

I presented the face-mirroring mechanism. During the presentation, a bug appeared: the eyebrow mechanism kept rotating without stopping. The cause is still unconfirmed, and the issue remains unresolved.

**Reflection**

Testing each facial movement separately helped me gradually refine the individual mechanisms. However, the eyebrow mechanism malfunctioned during the presentation. I suspect that multiple faces appearing in the camera frame at the same time may have triggered the bug, but I have not been able to reproduce it yet. This showed me that even when individual parts work, the complete system still needs more testing as a whole.

I also realized that using screws to assemble the outer shell added unnecessary complexity. A tab-and-slot joint would have made the enclosure easier to assemble, reduced the number of extra fasteners, and created a cleaner overall structure.

## Week-04

### Expressive Mechanics: Mechanical Research - Sep 15
This week, I started by exploring different types of mechanical movement because I was not yet sure what I wanted to make for the project. I looked through many examples of automata and focused on mechanisms such as cams, linkages, cranks, and ways of translating rotational motion into other forms of movement.

I also read Cabaret Mechanical Movement: Understanding Movement and Making Automata. The book helped me understand how relatively simple mechanical structures can generate expressive and sometimes surprisingly complex movements.
<p align = "center">
    <img src="./physical-computing/week4/src/book.png" width="342" alt="Cabaret Mechanical Movement">
</p>

Alongside these references, I watched different mechanical and automata examples on YouTube and made a few sketches of mechanisms that I found interesting. At this stage, I was mainly trying to build a vocabulary of mechanical movement and understand what kinds of motion I could potentially use in my own project.
<p align = "center">
    <img src="./physical-computing/week4/src/concept1.jpeg" width="342" alt="concept sketch1">
    <img src="./physical-computing/week4/src/concept2.jpeg" width="342" alt="concept sketch2">
</p>

### Expressive Mechanics: 3D-Printed Prototype Testing - Sep 18

After exploring different mechanical movements, I decided to create a face-mirroring mechanism with three servos. Each servo controls one facial feature: the eyelids, eyebrows, and mouth. 

I first tested each facial part separately before combining everything into one system. Since the makerspace was closed over the weekend and I could not use the laser cutter, I tested 3D-printed prototypes at home to check the geometry and servo motion.

One of the main problems was mechanical interference. As the servos rotated, the eyelids and mouth sometimes collided with nearby parts, preventing them from completing their full range of motion. I repeatedly adjusted the geometry, clearances, and servo angles to understand how much space each mechanism needed.
<p align = "center">
    <img src="./physical-computing/week5/src/failure.gif" width="342" alt="failure">
</p>

**Reflection**

The mechanism sketches helped me explore different types of movement, but the physical prototypes revealed many collisions I had not anticipated. This made me pay closer attention to the space each component actually needs throughout its full range of motion.

## Week-03

### Electronic - Sep 8
I built a **[simple interaction](./physical-computing/week3/electronics/ultrasounds-servo-motor/ultrasounds-servo-motor.ino)** using an ultrasonic sensor and a servo motor. The ultrasonic sensor measures the distance of an object, and the servo responds based on that distance.

When an object comes within 20 cm, the servo rotates to 90°. When the object moves away, it returns to 0°.
<p align = "center">
    <img src="./physical-computing/week3/src/ultrasound-servo-motor.gif" width="342" alt="ultrasound control servo motor demo">
    <img src="./physical-computing/week3/src/ultrasound-wiring-diagram.png" width="350" alt="ultrasound wiring diagram">
    <img src="./physical-computing/week3/src/ultrasound-schematic-diagram.png" width="370" alt="ultrasound schematic diagram">
</p>

### Fabrication - Sep 17
This week, I explored 3D printing through two different ring-making approaches.

The first one was a Flash ring, based on the ring I made in the previous laser-cutting exercise. Since the overall form was relatively simple, I drew the profile directly in a sketch and extruded it into a 3D form. After separating the ring into different parts, I added M2 holes at the connection points so that the pieces could be assembled after printing.
<p align = "center">
    <img src="./physical-computing/week3/src/ring_in_fusion.png" width="400" alt="ring in fusion360">
</p>

The second one was an organic ring made in Grasshopper. I started by creating a circle and extracting points along the curve, then rebuilt it with more points. I used random values to distribute the points around the circle and along the Z-axis, and moved them to create a second, more irregular circular profile. I then lofted the two profiles together to generate the main form. After that, I extracted the UV space of the surface, created a Voronoi pattern on it, and mapped the pattern back onto the curved geometry.
<p align = "center">
    <img src="./physical-computing/week3/src/ring_in_rhino.png" width="400" alt="ring in rhino">
    <br>
    <img src="./physical-computing/week3/src/3d_printing_ring.png" width="400" alt="3d printing ring">
</p>

## Week-02

### Electronic - Sep 1
This week, I started working with Arduino and learned the basic structure of an Arduino program, including `setup()` and `loop()`, digital output, delays, and serial communication.

I worked through two introductory exercises: **[Blink](./physical-computing/week2/electronics/blink/blink.ino)** and **[Hello World](./physical-computing/week2/electronics/hello-world/hello-world.ino)**, then combined the two concepts into a short **[exercise](./physical-computing/week2/electronics/combine-blink-hello-world/combine-blink-hello-world.ino)**.

<p align = "center">
    <img src="./physical-computing/week2/src/blink.gif" width="300" alt="Blink demo">
    <img src="./physical-computing/week2/src/hello-world.png" width="400" alt="Hello world demo">
</p>

---

I used an LDR to detect changes in ambient light and **[control an LED](./physical-computing/week2/electronics/ldr-control/ldr-control.ino)** based on the sensor value. The LDR circuit is connected to the analog input pin A0, and the LED turns on when the sensor value passes a selected threshold.

<p align = "center">
    <img src="./physical-computing/week2/src/ldr-control.gif" width="300" alt="LDR lightning control demo">
    <img src="./physical-computing/week2/src/ldr-control-circuit.png" width="225" alt="LDR breadboard wiring diagram">
</p>

**Take Away**
- An LDR needs to be read through an analog input pin.
- `A0` represents the analog input pin and can be stored as an `int`.
- `analogRead()` reads the analog value from the pin and returns an integer value.
- `Serial.println()` can be used to observe the sensor values and determine a suitable threshold.

---

I used multiple LEDs to create a **[back-and-forth light sequence](./physical-computing/week2/electronics/more-leds/more-leds.ino)**. The LEDs light up one by one in forward order, then reverse direction and return to the beginning.

<p align = "center">
    <img src="./physical-computing/week2/src/more-leds.gif" width="300" alt="multiplal lights demo">
    <img src="./physical-computing/week2/src/more-leds.png" width="225" alt="multiplal lights breadboard wiring diagram">
</p>

**Take Away**
- C++ arrays use `{}` instead of `[]` when initializing values.
- A basic C++ array does not have `.length()`.
- A `for` loop can be used to iterate through all LEDs in forward order.
- A second `for` loop can start from the end of the array and decrement the index to create the reverse sequence.
- Skipping the first and last LEDs in the reverse loop prevents the endpoint LEDs from lighting twice in a row.

### Fabrication - Sep 3

For this exercise, I wanted to make something more playful than a conventional ring, so I designed a Flash-inspired ring with a lightning-bolt element on top.

I first designed the parts as 2D profiles for laser cutting and adjusted the dimensions based on the thickness of the wood and the size of my finger. After cutting the pieces, I assembled them with small M2 screws and tested how the parts fit and move together.

<p align = "center">
    <img src="./physical-computing/week2/src/laser-cutting.gif" width="250" alt="laser cutter working gif">
    <img src="./physical-computing/week2/src/ring.png" width="350" alt="ring tear down diagram">
</p>
