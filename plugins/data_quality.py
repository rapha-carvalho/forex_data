from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class QualityError(Exception): pass

class DataQualityOperator(BaseOperator):

    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 quality_tests="",
                 *args, **kwargs):


        super(DataQualityOperator, self).__init__(*args, **kwargs)

        self.redshift_conn_id = redshift_conn_id
        self.quality_tests = quality_tests

    def execute(self, context):

        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        self.log.info('Running data quality tests')
        for test in self.quality_tests:
            self.log.info("Preparing to run test: {}".format(test['test_name']))
            self.log.info("Query result: {}".format(list(redshift.get_records(test['sql'])[0])[0]))
            if list(redshift.get_records(test['sql'])[0])[0] != test['expected_result']:
                raise QualityError("FAILED | Test: {}".format(test['test_name']))
            else:
                self.log.info("SUCCESS | Test: {}".format(test['test_name']))
