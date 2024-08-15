Handler handler = new Handler(); // to update UI  from background //thread.

Log.d("onRefresh= ", Thread.currentThread() + "");

Thread thread = new Thread() {

    @Override
    public void run() {
        try {
            Thread.sleep(1000);

            Log.d("onRefresh run= ", Thread.currentThread() + ""); // background thread
            
            handler.post(new Runnable() {
                @Override
                public void run() {
                    Log.d("onRefresh handler= ", Thread.currentThread() + ""); // update UI
                }
            });


        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
};
thread.start();