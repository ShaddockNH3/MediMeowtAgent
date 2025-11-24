import { service } from './login';

interface Base {
  code: string;
  msg: string;
}

export interface DoctorQueueResponse {
  base: Base;
  data: {
    record_ids: string[];
  };
}

export const getDoctorQueue = async (
  userId: string
): Promise<DoctorQueueResponse> => {
  return service.get('/doctor/queue', {
    params: { user_id: userId }
  });
};