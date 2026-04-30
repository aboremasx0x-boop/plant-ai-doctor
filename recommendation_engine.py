def smart_recommendation(diagnosis: dict) -> dict:
    pathogen_type = diagnosis.get("pathogen_type_en", "").lower()
    pathogen = diagnosis.get("pathogen", "")
    disease = diagnosis.get("disease_en", "")
    crop = diagnosis.get("crop_en", "")

    if "fungus" in pathogen_type or "oomycete" in pathogen_type:
        control = {
            "strategy_ar": "مكافحة حيوية فطرية",
            "bio_agents": [
                "Bacillus subtilis",
                "Bacillus velezensis",
                "Trichoderma harzianum",
                "Trichoderma asperellum"
            ],
            "plant_extracts": [
                "مستخلص قشر الرمان",
                "مستخلص المورينجا",
                "مستخلص النيم"
            ],
            "field_actions": [
                "إزالة الأجزاء المصابة",
                "تحسين التهوية",
                "تقليل الرطوبة والري العلوي",
                "عدم ترك بقايا نباتية مصابة في الحقل"
            ],
            "recommendation_text": (
                f"المرض المتوقع هو {disease} على {crop} والمسبب {pathogen}. "
                "بما أن المسبب فطري أو شبيه فطري، يوصى باستخدام مكافحة حيوية مثل "
                "Bacillus subtilis أو Trichoderma spp. مع مستخلصات نباتية داعمة مثل قشر الرمان أو النيم، "
                "مع تحسين التهوية وتقليل الرطوبة."
            )
        }

    elif "bacteria" in pathogen_type:
        control = {
            "strategy_ar": "إدارة حيوية وبكتيرية وقائية",
            "bio_agents": [
                "Bacillus subtilis",
                "Bacillus velezensis",
                "Pseudomonas fluorescens"
            ],
            "plant_extracts": [
                "مستخلص النيم",
                "مستخلص قشر الرمان",
                "مستخلص الثوم"
            ],
            "field_actions": [
                "إزالة النباتات أو الأجزاء شديدة الإصابة",
                "تعقيم أدوات القص",
                "تجنب الرش العلوي",
                "تحسين الصرف",
                "عدم نقل التربة من مناطق مصابة"
            ],
            "recommendation_text": (
                f"المرض المتوقع هو {disease} والمسبب {pathogen}. "
                "بما أن المسبب بكتيري، تكون المكافحة الحيوية مساعدة ووقائية أكثر من كونها علاجًا مباشرًا. "
                "يوصى باستخدام Bacillus spp. أو Pseudomonas fluorescens مع تعقيم الأدوات وتقليل الرطوبة."
            )
        }

    elif "virus" in pathogen_type:
        control = {
            "strategy_ar": "إدارة فيروسية وقائية",
            "bio_agents": [
                "لا يوجد علاج حيوي مباشر للفيروس داخل النبات"
            ],
            "plant_extracts": [
                "مستخلص النيم لتقليل الحشرات الناقلة",
                "مستخلصات طاردة للحشرات عند الحاجة"
            ],
            "field_actions": [
                "إزالة النباتات المصابة بشدة",
                "مكافحة الحشرات الناقلة مثل الذبابة البيضاء والمن",
                "استخدام شتلات سليمة",
                "إزالة الحشائش العائلة",
                "زراعة أصناف مقاومة إن وجدت"
            ],
            "recommendation_text": (
                f"المرض المتوقع فيروسي. لا توجد مكافحة حيوية مباشرة للفيروس داخل النبات، "
                "لذلك تركز التوصية على إزالة النباتات المصابة ومكافحة الحشرات الناقلة والوقاية."
            )
        }

    elif "nematode" in pathogen_type:
        control = {
            "strategy_ar": "مكافحة حيوية للنيماتودا",
            "bio_agents": [
                "Bacillus firmus",
                "Bacillus subtilis",
                "Paecilomyces lilacinus",
                "Pochonia chlamydosporia"
            ],
            "plant_extracts": [
                "مستخلص النيم",
                "مستخلص الثوم",
                "مستخلص الخروع"
            ],
            "field_actions": [
                "تحسين المادة العضوية في التربة",
                "استخدام دورة زراعية مناسبة",
                "تعقيم التربة إن أمكن",
                "استخدام شتلات سليمة",
                "تجنب نقل تربة ملوثة"
            ],
            "recommendation_text": (
                f"المسبب المتوقع نيماتودي. يوصى باستخدام عوامل حيوية مضادة للنيماتودا مثل "
                "Bacillus firmus أو Paecilomyces lilacinus، مع تحسين التربة والدورة الزراعية."
            )
        }

    else:
        control = {
            "strategy_ar": "توصية عامة لإدارة المرض",
            "bio_agents": [
                "Bacillus subtilis",
                "Trichoderma spp."
            ],
            "plant_extracts": [
                "مستخلص قشر الرمان",
                "مستخلص النيم"
            ],
            "field_actions": [
                "إزالة الأجزاء المصابة",
                "تحسين التهوية",
                "تقليل الرطوبة",
                "متابعة الإصابة ميدانيًا"
            ],
            "recommendation_text": (
                "لم يتم تحديد نوع المسبب بدقة، لذلك يوصى بإدارة عامة تشمل تقليل الرطوبة، "
                "إزالة الأجزاء المصابة، واستخدام مكافحة حيوية وقائية."
            )
        }

    return control