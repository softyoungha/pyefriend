from typing import Optional
from fastapi import APIRouter, Request, Response, status, HTTPException

from pyefriend.exceptions import NotConnectedException, AccountNotExistsException
from rebalancing.models import Report
from .schema import ReportInput, ReportOutput, PricesOutput, PlanOutput

r = APIRouter(prefix='/rebalance',
              tags=['v1'])


@r.post('/', response_model=ReportOutput)
async def create_report(request: ReportInput):
    """ pyefriend api 생성로 접속 테스트 """
    try:
        # set report
        report = Report(target=request.target,
                        test=request.test,
                        account=request.account,
                        password=request.password,
                        created_time=request.created_time,
                        prompt=False)

        # create api
        api = report.api

        # get context
        context = {
            'report_name': report.report_name,
            'created_time': report.created_time,
            'account': api.target_account,
            'is_vts': api.conn.IsVTS(),
        }

        # create report
        report.save(delete_if_exists=True)

        return context

    except NotConnectedException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    except AccountNotExistsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'{e.__name__}: \n{str(e)}')


@r.post('/{report_name}/prices', status_code=status.HTTP_201_CREATED)
async def refresh_prices(report_name: str, created_time: Optional[str]):
    """ DB 내 종목 가격 최신화('product' table) """
    report = Report.get(report_name=report_name, created_time=created_time)
    report.refresh_prices()

    return Response('Success', status_code=status.HTTP_201_CREATED)


@r.get('/{report_name}/prices', response_model=PricesOutput)
async def get_prices(report_name: str, created_time: Optional[str]):
    """ DB 내 종목 가격 조회('product' table) """
    report = Report.get(report_name=report_name, created_time=created_time)
    report.get_prices()
    return {
        'created_time': report.created_time
    }


@r.post('/{report_name}/plan', status_code=status.HTTP_201_CREATED)
async def make_plan(report_name: str, created_time: Optional[str]):
    """ 최신화된 가격을 토대로 리밸런싱 플랜 생성 """
    report = Report.get(report_name=report_name, created_time=created_time)
    report.make_plan()

    return Response('Success', status_code=status.HTTP_201_CREATED)


@r.get('/{report_name}/plan', response_model=PlanOutput)
async def get_plan(report_name: str, created_time: Optional[str]):
    """ 리밸런싱 플랜 조회 """
    report = Report.get(report_name=report_name, created_time=created_time)
    report.get_plan()
    return {
        'created_time': report.created_time
    }


@r.put('/{report_name}/plan', status_code=status.HTTP_201_CREATED)
async def adjust_plan(report_name: str, created_time: Optional[str]):
    """ 최신화된 가격을 토대로 리밸런싱 플랜 생성 """
    report = Report.get(report_name=report_name, created_time=created_time)
    report.adjust_plan()

    return Response('Success', status_code=status.HTTP_201_CREATED)


@r.post('/{report_name}/execute', status_code=status.HTTP_201_CREATED)
async def execute_plan(report_name: str, created_time: Optional[str]):
    """ 플랜 """
    report = Report.get(report_name=report_name, created_time=created_time)
    report.execute_plan()

    return Response('Success', status_code=status.HTTP_201_CREATED)
