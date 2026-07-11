# आधुनिक हिन्दी बाइबिल (A Modern Hindi Bible)

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
![Language](https://img.shields.io/badge/Language-Hindi%20%E0%A4%B9%E0%A4%BF%E0%A4%A8%E0%A5%8D%E0%A4%A6%E0%A5%80-orange)
![Status](https://img.shields.io/badge/Matthew-Complete-brightgreen)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-blue)

यह परियोजना पवित्र बाइबिल का एक नया, आधुनिक हिन्दी अनुवाद बनाने के लिए एक खुला-स्रोत (open-source) प्रयास है, जो आज के पाठकों के लिए स्पष्ट और समझने में आसान है।

**This is an open-source project to create a new, modern Hindi translation of the Holy Bible, built to be clear and easy to understand for today's readers.**

---

## 📖 Contents

- [Our Goal (हमारा लक्ष्य)](#-our-goal-a-bible-for-everyone-हमारा-लक्ष्य)
- [How We Are Doing It (हमारा तरीका)](#-how-we-are-doing-it-हमारा-तरीका)
- [Translation Progress (अनुवाद की प्रगति)](#-translation-progress-अनुवाद-की-प्रगति)
- [How It Is Organized (संरचना)](#-how-it-is-organized-संरचना)
- [How to Contribute (योगदान कैसे दें)](#-how-to-contribute-योगदान-कैसे-दें)
- [Sister Projects (सहयोगी परियोजनाएँ)](#-sister-projects-सहयोगी-परियोजनाएँ)
- [License (लाइसेंस)](#-license-लाइसेंस)

## 🎯 Our Goal: A Bible for Everyone (हमारा लक्ष्य)

भारत में लाखों लोग बाइबिल पढ़ना चाहते हैं, लेकिन एक बड़ी बाधा का सामना करते हैं: **भाषा।**

सबसे आम हिन्दी बाइबिल (पवित्र बाइबिल, OV) 1883 में लिखी गई थी। वह भाषा 140+ साल पुरानी, अर्काइक और पढ़ने में कठिन है।

**हमारा लक्ष्य सरल है:** परमेश्वर के वचन को एक ऐसी स्पष्ट, सुंदर और आधुनिक हिन्दी में प्रस्तुत करना, जिसे कोई भी, किसी भी शैक्षिक पृष्ठभूमि का व्यक्ति, आसानी से पढ़ और समझ सके।

## 🤝 How We Are Doing It (हमारा तरीका)

**यह एक मूल अनुवाद है, कोई कॉपी नहीं है।**

हमारा अनुवाद कार्य सार्वजनिक डोमेन (public domain) स्रोतों पर आधारित है, जिसमें मूल यूनानी पांडुलिपियाँ और वर्ल्ड इंग्लिश बाइबिल (WEB) शामिल हैं। यह हमें एक ऐसा अनुवाद बनाने की स्वतंत्रता देता है जो:

- **सटीक (Accurate):** मूल अर्थ के प्रति वफादार।
- **आधुनिक (Modern):** पुरानी, भ्रामक भाषा के बजाय आज की हिन्दी का उपयोग करना।
- **सुलभ (Accessible):** सभी के लिए पढ़ने में आसान।

## 📊 Translation Progress (अनुवाद की प्रगति)

| Book (पुस्तक) | Chapters | Status |
| --- | --- | --- |
| Matthew (मत्ती) | 28 | ✅ Complete |
| Other New Testament books | — | 🔜 Planned |

नए अध्याय और पुस्तकें जोड़ने में मदद के लिए स्वयंसेवकों का स्वागत है। *We welcome volunteers to help add new chapters and books.*

## 🗂️ How It Is Organized (संरचना)

प्रत्येक पुस्तक का अपना फ़ोल्डर होता है, और हर अध्याय एक अलग `.yaml` फ़ाइल में रखा जाता है (उदाहरण: `Matthew/1.yaml`)।

Each book has its own folder, and every chapter is stored as a separate `.yaml` file (for example, `Matthew/1.yaml`) with a simple, readable structure:

```yaml
book: "..."
chapter: 1
verses:
  - verse: 1
    text: "..."
```

## 🙏 How to Contribute (योगदान कैसे दें)

यह एक सामुदायिक प्रयास है! आप मौजूदा अनुवादों की समीक्षा करके, त्रुटियों को ठीक करके, या नए अध्यायों का अनुवाद करके मदद कर सकते हैं।

*This is a community effort! You can help by reviewing existing translations, fixing errors, or translating new chapters.*

आरंभ करने के लिए:

1. इस रिपॉजिटरी को **fork** करें। *(Fork this repository.)*
2. अपने परिवर्तन करें। *(Make your changes.)*
3. एक **Pull Request** सबमिट करें। *(Submit a Pull Request.)*

आप कोई प्रश्न या सुझाव साझा करने के लिए एक [issue](../../issues) भी खोल सकते हैं। *You can also open an [issue](../../issues) to ask a question or share a suggestion.*

⭐ यदि यह परियोजना आपके लिए उपयोगी है, तो कृपया इसे **star** करें और दूसरों के साथ साझा करें। *If this project helps you, please star it and share it with others.*

## 🌏 Sister Projects (सहयोगी परियोजनाएँ)

यह परियोजना PrimeBible की खुली अनुवाद परियोजनाओं के परिवार का हिस्सा है:

- [Saraiki Modern Literal Translation](https://github.com/primebible/Saraiki-Modern-Literal-Translation)
- [Northern Hindko Modern Literal Translation](https://github.com/primebible/Northern-Hindko-Modern-Literal-Translation)

## 📜 License (लाइसेंस)

This work is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

To use this work, you must give credit to [https://primebible.com](https://primebible.com).
