from startup import Startup
from runtime.builder import ApplicationBuilder
from runtime.dependency_injection import ServiceStorage
from runtime.pipeline import Pipeline

if __name__ == "__main__":
    startup = Startup()
    app_builder = ApplicationBuilder()
    services = ServiceStorage()
    startup.configure_services()
    startup.configure(app_builder)

    pipeline = Pipeline()
    pipeline.configure(app_builder)
    pipeline.start_polling()
