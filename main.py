import runtime.dependency_injection
import runtime.builder
import startup
import runtime.pipeline

if __name__ == "__main__":
    startup = startup.Startup()
    app_builder = runtime.builder.ApplicationBuilder()
    services = runtime.dependency_injection.ServiceCollection()
    startup.configure_services(services)
    startup.configure(app_builder)

    pipeline = runtime.pipeline.Pipeline()
    pipeline.configure(app_builder, services)
    pipeline.start_polling()
