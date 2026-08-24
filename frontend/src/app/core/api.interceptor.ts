import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, finalize, throwError } from 'rxjs';
import { LoadingService } from './loading.service';

export const apiInterceptor: HttpInterceptorFn = (request, next) => {
  const loading = inject(LoadingService);
  const apiRequest = request.url.startsWith('/')
    ? request.clone({ url: `/api/v1${request.url}`, withCredentials: true })
    : request;
  loading.start();
  return next(apiRequest).pipe(
    catchError((error: HttpErrorResponse) => throwError(() => error)),
    finalize(() => loading.stop()),
  );
};

