<p align="center">
  <img src=".\frontend\front\public\static\Logo.png" alt="NagTODO Logo" width="300" />
</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/Language-TypeScript%20%7C%20Python-FDE68A?logo=python&logoColor=black" alt="Language: TypeScript | Python" />
  <img src="https://img.shields.io/badge/Frontend-React%20%7C%20Vite-BAE6FD?logo=react&logoColor=black" alt="Frontend: React | Vite" />
  <img src="https://img.shields.io/badge/Backend-FastAPI-BBF7D0?logo=fastapi&logoColor=black" alt="Backend: FastAPI" />
  <img src="https://img.shields.io/badge/DB-MySQL-BFDBFE?logo=mysql&logoColor=black" alt="DB: MySQL" />
  <br />
  <img src="https://img.shields.io/badge/Embedding-multilingual--e5--small-E9D5FF" alt="Embedding: multilingual-e5-small" />
  <img src="https://img.shields.io/badge/LLM-Qwen2.5:7b-FBCFE8" alt="LLM: Qwen2.5:7b" />
  <img src="https://img.shields.io/badge/Workflow-LangGraph-B5F5EC" alt="Workflow: LangGraph" />
  <br />
  <img src="https://img.shields.io/badge/Vector%20Search-FAISS-BAE6FD" alt="Vector Search: FAISS" />
  <img src="https://img.shields.io/badge/LLM%20Runtime-Ollama-E5E7EB" alt="LLM Runtime: Ollama" />
</p>

<br />

[NagTODO 시연 영상 보러가기](https://youtu.be/S1QiVu4N3s8)

<br />

사람들은 해야 할 일을 몰라서 미루는 게 아닙니다.  
알면서도 안 하기 때문에 미룹니다.

기존 Todo 앱은 할 일을 기록하고, 완료 여부를 체크하는 데 집중합니다. 하지만 기록만으로는 행동이 바뀌지 않습니다. 해야 한다는 걸 알고 있어도, 귀찮고 미루고 싶고 나중으로 넘기고 싶을 때가 많기 때문입니다.

NagTODO는 이 지점에서 출발한 **잔소리형 Todo 서비스**입니다.

단순히 알림을 보내는 것이 아니라, 사용자가 할 일을 미루지 않도록 계속 건드리고, 과거의 수행 패턴을 분석해 더 잘 실천할 수 있는 방향을 제안합니다. 기록에서 끝나는 Todo가 아니라, 실제 행동으로 이어지게 만드는 Todo를 목표로 합니다.

<br />

## 서비스 소개

NagTODO는 사용자의 할 일 수행 패턴을 AI가 분석해, 필요할 때마다 거슬릴 정도로 건방진 잔소리를 던지는 Todo 서비스입니다.

사용자가 새로운 할 일을 등록하면, NagTODO는 과거에 비슷한 일을 얼마나 성공했는지 확인합니다. 반복적으로 실패했던 유형이라면 그냥 조용히 응원하지 않습니다. "이거 또 미루려고?", "예전에도 비슷한 거 실패하지 않았나?"처럼 사용자가 외면하고 싶은 지점을 일부러 찌릅니다.

한 달 동안 쌓인 기록도 적당히 예쁘게 포장하지 않습니다. 어떤 유형의 일을 자주 미뤘는지, 어떤 패턴으로 실패가 반복됐는지 보여주고, 사용자가 스스로 핑계 대던 부분을 다시 마주하게 만듭니다.

NagTODO의 잔소리는 다정한 위로보다 행동을 끌어내는 자극에 가깝습니다. 조금 짜증나도, 계속 신경 쓰이게 만들어 결국 할 일을 하게 만드는 것이 이 서비스의 포인트입니다.


<br />

## 투칸(To-Can)

<p align="center">
  <img src=".\frontend\front\public\static\cloth\인사_Default.png" width="180" />
</p>

투칸(To-Can)은 사용자를 재촉하고 잔소리해가며, 할 일(To)을 완료(Can)하도록 도와주는 NagTODO의 캐릭터입니다.

계속 미루고 싶은 순간에도 옆에서 한마디씩 건네며 사용자가 다시 할 일로 돌아오도록 돕습니다. 단순히 차가운 알림을 보내는 것이 아니라, 친구처럼 말을 걸고 반응하는 존재로 설계했습니다.

투칸 캐릭터는 Google Gemini를 사용하여 제작하였습니다.

<br />

## 왜 NagTODO인가

Todo 앱을 열어 할 일을 적는 것만으로는 충분하지 않습니다.

문제는 "무엇을 해야 하는가"가 아니라 "왜 계속 안 하는가"에 있습니다. NagTODO는 사용자가 스스로 외면하던 패턴을 다시 보여주고, 적절한 압박감과 심리적 책임감을 만들어 실행을 유도합니다.

기존 Todo 앱이 수동적인 일정 관리 도구라면, NagTODO는 사용자의 행동 변화를 이끄는 능동적인 Todo 서비스입니다.

<br />

## 핵심 기능

### AI 잔소리 간섭

<p align="center">
  <img src=".\images\todo_add.png" width="30%" />
  <img src=".\images\todo_interference.png" width="30%" />
</p>

할 일을 등록하는 순간, AI가 비슷한 과거 task를 분석합니다.

- 비슷한 일을 예전에 얼마나 성공했는지 확인
- 개인 성공률과 전체 성공률을 기반으로 피드백 제공
- 반복 실패 가능성이 있는 task에 대해 상황에 맞는 잔소리 제공
- 사용자가 계획을 더 현실적으로 조정하도록 유도

<br />

### 월간 회고 리포트

<p align="center">
  <img src=".\images\monthly_report_1.png" width="30%" />
  <img src=".\images\monthly_report_2.png" width="30%" />
  <img src=".\images\monthly_report_3.png" width="30%" />
</p>

한 달 동안의 Todo 기록을 AI가 분석해 회고 리포트를 생성합니다.

- 완료율 중심이 아닌 실패 패턴 중심 분석
- 반복적으로 미룬 task 유형 파악
- 비슷한 실패 task를 묶어 원인과 경향 요약
- 다음 달 목표 달성을 위한 개선 방향 제안

<br />

### 친구 기능

<p align="center">
  <img src=".\images\friendlist.png" width="30%" />
  <img src=".\images\friend_todo.png" width="30%" />
</p>

친구를 추가하면 서로의 Todo를 확인할 수 있습니다.

- 친구의 Todo 진행 상황 확인
- 서로 미루고 있는 task를 보며 자연스럽게 자극 받기
- 혼자 관리하는 Todo가 아니라 함께 실천하는 Todo 경험 제공

<br />

### 출석 보상과 코스튬

<p align="center">
  <img src=".\images\char_default.png" width="30%" />
  <img src=".\images\char_cro.png" width="30%" />
</p>

NagTODO는 잔소리만 하는 서비스가 아닙니다. 사용자가 매일 다시 들어오고, 꾸준히 할 일을 관리할 수 있도록 보상 체계를 제공합니다.

- 매일 출석체크 가능
- 출석을 이어가면 보상 획득
- 보상으로 투칸의 코스튬 캐릭터 해금
- 해금한 코스튬으로 내 캐릭터 변경 가능

코스튬을 입은 투칸들은 출석 보상으로 제공됩니다. 사용자는 잔소리를 듣기만 하는 것이 아니라, 꾸준히 돌아온 만큼 새로운 캐릭터를 모으는 재미도 얻을 수 있습니다.

<br />

### 홈 화면 커스터마이징

<p align="center">
  <img src=".\images\home_bgimg.png" width="30%" />
  <img src=".\images\home_music.png" width="30%" />
</p>

사용자는 홈 화면에서 원하는 배경과 BGM을 설정할 수 있습니다.

잔소리형 Todo라는 핵심 경험은 유지하되, 사용자가 자신의 취향에 맞는 분위기에서 서비스를 사용할 수 있도록 배경 이미지와 음악 선택 기능을 제공합니다.

<br />

## NagTODO가 만드는 경험

NagTODO는 사용자가 할 일을 잊지 않게 하는 데서 멈추지 않습니다.  
해야 한다는 걸 알면서도 미루는 순간에 개입하고, 사용자가 스스로 행동을 수정할 수 있도록 돕습니다.

조금 귀찮더라도 누가 계속 옆에서 뭐라고 하면 결국 하게 되는 것처럼.  
NagTODO는 사용자의 일상 속에서 실천력을 높이는 AI 기반 잔소리 파트너를 지향합니다.

그리고 그 잔소리가 마냥 불쾌한 경험으로 끝나지 않도록, 캐릭터와 보상, 커스터마이징 요소를 함께 제공합니다. NagTODO는 압박감과 재미 사이의 균형을 통해 사용자가 꾸준히 돌아오고, 결국 행동하게 만드는 Todo 서비스를 목표로 합니다.
