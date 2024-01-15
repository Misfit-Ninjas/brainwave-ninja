from backend.services.neurons.config import future_quarters


class TestRun:
    def test_it_should_return_the_config(self):
        config = future_quarters.Config(number_of_quarters=7)
        assert future_quarters.run(config) == config
