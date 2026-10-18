"""Patient-facing error text; internal exceptions and service responses stay private."""
def error_language(request):
    value=request.query_params.get('lang') or request.headers.get('accept-language','en').split(',')[0].split('-')[0]
    return value if value in ['en','hi','mr'] else 'en'

def error_text(request, status, detail):
    lang=error_language(request)
    if lang=='en': return detail
    if status==422 and '/doctors' in request.url.path and isinstance(detail,str) and any(word in detail.lower() for word in ['snapshot','locality','ambiguous','pin']):
        return {'hi':'स्थान अस्पष्ट है या स्थानीय OSM स्नैपशॉट में उपलब्ध नहीं है। नज़दीकी ज्ञात स्थान, पिन या GPS का उपयोग करें।','mr':'ठिकाण अस्पष्ट आहे किंवा स्थानिक OSM स्नॅपशॉटमध्ये नाही. जवळचे ज्ञात ठिकाण, पिन किंवा GPS वापरा.'}[lang]
    if status==422:
        renal = isinstance(detail,str) and any(word in detail.lower() for word in ['dietitian','clinician','kidney','food plan','meal','allerg','restriction'])
        if renal: return {'hi':'इन आहार ज़रूरतों के लिए डॉक्टर या आहार विशेषज्ञ की सलाह आवश्यक है। कोई प्रतिबंध नहीं हटाया गया और योजना नहीं बनाई गई।','mr':'या आहार गरजांसाठी डॉक्टर किंवा आहारतज्ज्ञांचा सल्ला आवश्यक आहे. कोणतेही निर्बंध काढलेले नाहीत आणि योजना तयार केलेली नाही.'}[lang]
    messages={
        400:['अनुरोध मान्य नहीं है। जानकारी जाँचें।','विनंती वैध नाही. माहिती तपासा.'],
        401:['सत्र समाप्त या अमान्य है। फिर साइन इन करें।','सत्र संपले किंवा अवैध आहे. पुन्हा साइन इन करा.'],
        403:['अनुमति या स्पष्ट सहमति आवश्यक है।','परवानगी किंवा स्पष्ट संमती आवश्यक आहे.'],
        404:['माँगी गई जानकारी उपलब्ध नहीं है।','मागितलेली माहिती उपलब्ध नाही.'],
        413:['फ़ाइल या अनुरोध निर्धारित आकार से बड़ा है।','फाइल किंवा विनंती ठरलेल्या आकारापेक्षा मोठी आहे.'],
        422:['जानकारी अधूरी, अस्पष्ट या असमर्थित है। फ़ाइल और उत्तर जाँचें।','माहिती अपूर्ण, अस्पष्ट किंवा असमर्थित आहे. फाइल आणि उत्तरे तपासा.'],
        429:['बहुत अधिक अनुरोध हैं। थोड़ी देर बाद कोशिश करें।','खूप विनंत्या आहेत. थोड्या वेळाने प्रयत्न करा.'],
        503:['सेवा उपलब्ध या कॉन्फ़िगर नहीं है। बाद में कोशिश करें।','सेवा उपलब्ध किंवा कॉन्फिगर केलेली नाही. नंतर प्रयत्न करा.']}
    values=messages.get(status,['अनुरोध पूरा नहीं हुआ। फिर कोशिश करें।','विनंती पूर्ण झाली नाही. पुन्हा प्रयत्न करा.'])
    return values[0 if lang=='hi' else 1]
