from config import settings
from guardian.guardian import FineTunedBERT

anti_fraud = FineTunedBERT(settings.guardian.path)
