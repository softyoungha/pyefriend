import os
from typing import Optional, List
from fastapi import APIRouter, Request, Response, status, HTTPException
from fastapi.responses import FileResponse

from pyefriend.exceptions import NotConnectedException, AccountNotExistsException
from rebalancing.models.report import Status, Report
from .schema import ReportInput, ReportOutput, PricesOutput, PlanOutput

r = APIRouter(prefix='/report',
              tags=['v1/report'])


@r.post('/', response_model=ReportOutput)
async def create_report(request: ReportInput):
    """ pyefriend api 생성로 접속 테스트 """
    try:
        # set report
        report: Report = Report(target=request.target,
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
                            detail=f'{e.__class__.__name__}: \n{str(e)}')


@r.post('/{report_name}/prices', status_code=status.HTTP_201_CREATED)
async def refresh_prices(report_name: str, created_time: Optional[str] = None):
    """ DB 내 종목 가격 최신화('product' table) """
    report: Report = Report.get(report_name=report_name, created_time=created_time)
    report.refresh_prices()
    return Response('Success', status_code=status.HTTP_201_CREATED)


@r.get('/{report_name}/prices', response_model=List[PricesOutput])
async def get_prices(report_name: str, created_time: Optional[str] = None):
    """ DB 내 종목 가격 조회('product' table) """
    report: Report = Report.get(report_name=report_name, created_time=created_time)
    return report.get_prices()


@r.post('/{report_name}/plan', status_code=status.HTTP_201_CREATED)
async def make_plan(report_name: str, created_time: Optional[str] = None):
    """ 최신화된 가격을 토대로 리밸런싱 플랜 생성 """
    report: Report = Report.get(report_name=report_name,
                                created_time=created_time)
    report.make_plan()
    return Response('Success', status_code=status.HTTP_201_CREATED)


@r.get('/{report_name}/plan', response_class=FileResponse)
async def get_plan(report_name: str,
                   created_time: Optional[str] = None,
                   summary: Optional[bool] = False):
    """
    ### 리밸런싱 플랜 조회
    - report_name: 리포트명
    - created_time: None일 경우 가장 최신 날짜를 가져옴
    - summary: True일 경우 요약정보, False일 경우 상세정보
    """
    report: Report = Report.get(report_name=report_name,
                                created_time=created_time,
                                statuses=[Status.PLANNING, Status.EXECUTED])

    if summary:
        path = report.summary_path
    else:
        path = report.plan_path

    if not os.path.exists(path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    response = FileResponse(path,
                            media_type='text/csv',
                            filename=report.name)
    return response


@r.put('/{report_name}/plan', status_code=status.HTTP_201_CREATED)
async def adjust_plan(report_name: str, created_time: Optional[str] = None):
    """ 최신화된 가격을 토대로 리밸런싱 플랜 생성 """
    report: Report = Report.get(report_name=report_name,
                                created_time=created_time,
                                statuses=[Status.PLANNING, Status.EXECUTED])
    report.adjust_plan()

    return Response('Success', status_code=status.HTTP_201_CREATED)


@r.post('/{report_name}/execute', status_code=status.HTTP_201_CREATED)
async def execute_plan(report_name: str, created_time: Optional[str] = None):
    """ 플랜 """
    report: Report = Report.get(report_name=report_name,
                                created_time=created_time,
                                statuses=[Status.PLANNING, Status.EXECUTED])
    report.execute_plan()

    return Response('Success', status_code=status.HTTP_201_CREATED)
