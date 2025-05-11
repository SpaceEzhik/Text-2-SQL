from config import settings
from guardian.guardian import FineTunedBERT, DummyBERT

anti_fraud = (
    FineTunedBERT(settings.guardian.path) if settings.guardian.enabled else DummyBERT()
)
