import { configureStore } from '@reduxjs/toolkit'
import examSlice from './exam/examSlice'
import studentSlice from './student/studentSlice'

export const store = configureStore({
  reducer: {
    exam: examSlice,
    student: studentSlice,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
