-- Bảng profiles lưu trữ thông tin về số token của người dùng
-- Nó sẽ tự động liên kết với hệ thống Supabase Auth (auth.users)
create table public.profiles (
  id uuid references auth.users not null primary key,
  email text,
  free_credits int default 3 not null,
  paid_tokens int default 0 not null,
  gift_codes_used text[] default '{}' not null,
  last_used_date date default current_date not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Nếu bảng profiles đã tồn tại, chạy lệnh ALTER thay vì CREATE:
-- ALTER TABLE public.profiles ADD COLUMN IF NOT EXISTS gift_codes_used text[] DEFAULT '{}' NOT NULL;

-- Bật Row Level Security (RLS) để bảo mật
alter table public.profiles enable row level security;

-- Cho phép người dùng đọc thông tin của chính họ
create policy "Users can view own profile."
  on profiles for select
  using ( auth.uid() = id );

-- Cho phép hệ thống/service role cập nhật profile (khi chạy trên backend)
create policy "Service role can update profiles"
  on profiles for update
  using ( true );

-- Trigger tự động tạo profile khi một người dùng mới đăng ký qua Supabase Auth
create function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email, free_credits, paid_tokens)
  values (new.id, new.email, 3, 0);
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ==========================================
-- Bảng transactions lưu trữ lịch sử nạp tiền từ SePay Webhook
create table public.transactions (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) not null,
  amount_vnd int not null,
  tokens_added int not null,
  transaction_code text unique not null, -- Mã giao dịch của ngân hàng (giúp chống nạp trùng 2 lần)
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Bật RLS
alter table public.transactions enable row level security;

-- Cho phép user xem lịch sử nạp tiền của mình
create policy "Users can view own transactions"
  on transactions for select
  using ( auth.uid() = user_id );

-- Cho phép hệ thống/service role insert giao dịch mới từ Webhook
create policy "Service role can insert transactions"
  on transactions for insert
  with check ( true );
