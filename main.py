from startup import Startup
from runtime.configuration import Configuration
from runtime.pipeline import Pipeline

if __name__ == "__main__":
    startup = Startup()
    configuration = Configuration()
    startup.configure(configuration)

    pipeline = Pipeline()
    pipeline.configure(configuration)
    pipeline.start_polling()
